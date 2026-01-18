from sqlalchemy import func
from src.models.user import db
from src.models.material import Material, Supplier
from src.models.comparison import CanonicalMaterial, MaterialVariant


def get_material_comparison(material_id):
    material = Material.query.get(material_id)
    if not material:
        return None

    if material.variant:
        canonical = material.variant.canonical
        variants = MaterialVariant.query.filter(
            MaterialVariant.canonical_material_id == canonical.id
        ).all()
    else:
        variants = find_similar_materials(material)

    if not variants:
        return {
            'material': material.to_dict(),
            'comparisons': [],
            'price_range': {'min': material.price, 'max': material.price, 'avg': material.price},
            'best_value': None
        }

    comparisons = []
    prices = []

    for variant in variants:
        if variant.price is not None:
            prices.append(variant.price)
        comparisons.append({
            'supplier': variant.supplier.to_dict() if variant.supplier else None,
            'price': variant.price,
            'unit': variant.unit,
            'lead_time_days': variant.lead_time_days,
            'availability': variant.availability,
            'minimum_order': variant.minimum_order,
            'material_id': variant.material_id,
            'last_updated': variant.last_updated.isoformat() if variant.last_updated else None
        })

    comparisons.sort(key=lambda x: x['price'] if x['price'] is not None else float('inf'))

    if prices:
        price_range = {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices)
        }
    else:
        price_range = {'min': None, 'max': None, 'avg': None}

    best_value = determine_best_value(comparisons)

    return {
        'material': material.to_dict(),
        'comparisons': comparisons,
        'price_range': price_range,
        'best_value': best_value
    }


def find_similar_materials(material):
    similar = Material.query.filter(
        Material.category == material.category,
        Material.id != material.id
    ).all()

    variants = []
    for m in similar:
        variants.append(MaterialVariant(
            supplier_id=m.supplier_id,
            supplier=m.supplier,
            material_id=m.id,
            price=m.price,
            unit=m.unit,
            lead_time_days=m.lead_time_days,
            availability=m.availability,
            minimum_order=m.minimum_order
        ))

    variants.append(MaterialVariant(
        supplier_id=material.supplier_id,
        supplier=material.supplier,
        material_id=material.id,
        price=material.price,
        unit=material.unit,
        lead_time_days=material.lead_time_days,
        availability=material.availability,
        minimum_order=material.minimum_order
    ))

    return variants


def determine_best_value(comparisons):
    if not comparisons:
        return None

    scored = []
    for c in comparisons:
        score = 0
        price = c.get('price') or 0
        lead_time = c.get('lead_time_days') or 999
        availability = c.get('availability') or ''

        if price and price > 0:
            score += 50 * (1 / price)

        if lead_time and lead_time < 7:
            score += 30
        elif lead_time and lead_time < 14:
            score += 20
        elif lead_time and lead_time < 30:
            score += 10

        if availability == 'in_stock':
            score += 20
        elif availability == 'limited_stock':
            score += 10

        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]

    reasons = []
    valid_prices = [c.get('price') for c in comparisons if c.get('price') is not None]
    valid_lead_times = [c.get('lead_time_days') for c in comparisons if c.get('lead_time_days') is not None]

    if valid_prices and best.get('price') == min(valid_prices):
        reasons.append('Lowest price')
    if valid_lead_times and best.get('lead_time_days') == min(valid_lead_times):
        reasons.append('Fastest delivery')
    if best.get('availability') == 'in_stock':
        reasons.append('Available now')

    return {
        'supplier_id': best.get('supplier', {}).get('id') if best.get('supplier') else None,
        'material_id': best.get('material_id'),
        'reason': ', '.join(reasons) if reasons else 'Best overall value'
    }


def create_canonical_material(name, category, subcategory=None, specifications=None, description=None):
    canonical = CanonicalMaterial(
        name=name,
        category=category,
        subcategory=subcategory,
        specifications=specifications,
        description=description
    )
    db.session.add(canonical)
    db.session.commit()
    return canonical


def add_variant_to_canonical(canonical_id, supplier_id, price, unit, material_id=None,
                              lead_time_days=None, availability=None, minimum_order=None):
    variant = MaterialVariant(
        canonical_material_id=canonical_id,
        supplier_id=supplier_id,
        material_id=material_id,
        price=price,
        unit=unit,
        lead_time_days=lead_time_days,
        availability=availability,
        minimum_order=minimum_order
    )
    db.session.add(variant)
    db.session.commit()
    return variant


def get_price_statistics(canonical_id):
    stats = db.session.query(
        func.min(MaterialVariant.price).label('min_price'),
        func.max(MaterialVariant.price).label('max_price'),
        func.avg(MaterialVariant.price).label('avg_price'),
        func.count(MaterialVariant.id).label('variant_count')
    ).filter(
        MaterialVariant.canonical_material_id == canonical_id
    ).first()

    return {
        'min_price': float(stats.min_price) if stats.min_price else 0,
        'max_price': float(stats.max_price) if stats.max_price else 0,
        'avg_price': float(stats.avg_price) if stats.avg_price else 0,
        'variant_count': stats.variant_count
    }
