import asyncio
from datetime import datetime, timedelta
from src.celery_app import celery_app
from src.models.user import db
from src.models.material import DataProvider, PriceSource, SyncJob, Material
from src.integrations import get_provider_adapter
from src.integrations.demo_provider import DemoProviderAdapter


def get_flask_app():
    from src.main import app
    return app


@celery_app.task(bind=True)
def sync_provider(self, provider_id: int, job_type: str = 'full'):
    with get_flask_app().app_context():
        provider = DataProvider.query.get(provider_id)
        if not provider or not provider.is_active:
            return {'error': 'Provider not found or inactive'}

        sync_job = SyncJob(
            provider_id=provider_id,
            job_type=job_type,
            status='running',
            started_at=datetime.utcnow()
        )
        db.session.add(sync_job)
        db.session.commit()

        try:
            config = {
                'name': provider.name,
                'base_url': provider.base_url,
                'api_key': provider.api_key_encrypted,
                'config': provider.config
            }

            adapter = get_provider_adapter(provider.name, config)
            if not adapter:
                raise ValueError(f"No adapter found for provider: {provider.name}")

            result = asyncio.run(adapter.fetch_prices(limit=100))

            if result.success and result.prices:
                for price_data in result.prices:
                    material = Material.query.filter_by(name=price_data.name).first()
                    if material:
                        price_source = PriceSource(
                            material_id=material.id,
                            provider_id=provider_id,
                            external_id=price_data.external_id,
                            price=price_data.price,
                            unit=price_data.unit,
                            currency=price_data.currency,
                            confidence_score=price_data.confidence_score,
                            source_url=price_data.source_url,
                            raw_data=price_data.raw_data,
                            fetched_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(hours=24)
                        )
                        db.session.add(price_source)

                db.session.commit()

            sync_job.status = 'completed'
            sync_job.completed_at = datetime.utcnow()
            sync_job.items_processed = result.items_processed
            sync_job.items_failed = result.items_failed

            provider.last_sync_at = datetime.utcnow()
            db.session.commit()

            return {
                'status': 'completed',
                'items_processed': result.items_processed,
                'items_failed': result.items_failed
            }

        except Exception as e:
            sync_job.status = 'failed'
            sync_job.completed_at = datetime.utcnow()
            sync_job.error_message = str(e)
            db.session.commit()
            raise


@celery_app.task
def sync_volatile_materials():
    with get_flask_app().app_context():
        providers = DataProvider.query.filter_by(is_active=True).all()
        volatile_categories = ['Steel', 'Lumber']

        for provider in providers:
            if provider.config.get('supports_volatile', False):
                sync_provider.delay(provider.id, 'incremental')

        return {'message': f'Queued {len(providers)} providers for volatile sync'}


@celery_app.task
def sync_full_catalog():
    with get_flask_app().app_context():
        providers = DataProvider.query.filter_by(is_active=True).all()

        for provider in providers:
            hours_since_sync = 999
            if provider.last_sync_at:
                hours_since_sync = (datetime.utcnow() - provider.last_sync_at).total_seconds() / 3600

            if hours_since_sync >= provider.sync_interval_hours:
                sync_provider.delay(provider.id, 'full')

        return {'message': f'Checked {len(providers)} providers for full sync'}


@celery_app.task
def cleanup_expired_prices():
    with get_flask_app().app_context():
        expired = PriceSource.query.filter(
            PriceSource.expires_at < datetime.utcnow(),
            PriceSource.is_valid == True
        ).all()

        for price_source in expired:
            price_source.is_valid = False

        db.session.commit()

        return {'message': f'Marked {len(expired)} price sources as invalid'}
