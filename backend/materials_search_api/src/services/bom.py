from datetime import datetime
from typing import List, Optional, Dict, Any
import io
import csv
from src.models.user import db
from src.models.material import Material
from src.models.bom import BillOfMaterials, BOMItem


def create_bom(user_id: int, name: str, description: str = None, project_id: int = None) -> BillOfMaterials:
    bom = BillOfMaterials(
        user_id=user_id,
        name=name,
        description=description,
        project_id=project_id,
        status='draft'
    )
    db.session.add(bom)
    db.session.commit()
    return bom


def get_user_boms(user_id: int, status: str = None) -> List[BillOfMaterials]:
    query = BillOfMaterials.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(BillOfMaterials.updated_at.desc()).all()


def get_bom_by_id(bom_id: int, user_id: int) -> Optional[BillOfMaterials]:
    return BillOfMaterials.query.filter_by(id=bom_id, user_id=user_id).first()


def update_bom(bom: BillOfMaterials, name: str = None, description: str = None,
               status: str = None, project_id: int = None) -> BillOfMaterials:
    if name is not None:
        bom.name = name
    if description is not None:
        bom.description = description
    if status is not None:
        bom.status = status
    if project_id is not None:
        bom.project_id = project_id
    db.session.commit()
    return bom


def delete_bom(bom: BillOfMaterials) -> None:
    db.session.delete(bom)
    db.session.commit()


def add_item_to_bom(bom_id: int, material_id: int, quantity: float,
                    notes: str = None, sort_order: int = None) -> Optional[BOMItem]:
    material = Material.query.get(material_id)
    if not material:
        return None

    max_order = db.session.query(db.func.max(BOMItem.sort_order)).filter_by(bom_id=bom_id).scalar() or 0

    item = BOMItem(
        bom_id=bom_id,
        material_id=material_id,
        quantity=quantity,
        unit_price_snapshot=material.price,
        notes=notes,
        sort_order=sort_order if sort_order is not None else max_order + 1
    )
    db.session.add(item)
    db.session.commit()
    return item


def update_bom_item(item: BOMItem, quantity: float = None, notes: str = None,
                    sort_order: int = None, refresh_price: bool = False) -> BOMItem:
    if quantity is not None:
        item.quantity = quantity
    if notes is not None:
        item.notes = notes
    if sort_order is not None:
        item.sort_order = sort_order
    if refresh_price and item.material:
        item.unit_price_snapshot = item.material.price
    db.session.commit()
    return item


def remove_item_from_bom(item: BOMItem) -> None:
    db.session.delete(item)
    db.session.commit()


def get_bom_item(item_id: int, bom_id: int) -> Optional[BOMItem]:
    return BOMItem.query.filter_by(id=item_id, bom_id=bom_id).first()


def duplicate_bom(bom: BillOfMaterials, new_name: str = None) -> BillOfMaterials:
    new_bom = BillOfMaterials(
        user_id=bom.user_id,
        project_id=bom.project_id,
        name=new_name or f"{bom.name} (Copy)",
        description=bom.description,
        status='draft'
    )
    db.session.add(new_bom)
    db.session.flush()

    for item in bom.items:
        new_item = BOMItem(
            bom_id=new_bom.id,
            material_id=item.material_id,
            quantity=item.quantity,
            unit_price_snapshot=item.unit_price_snapshot,
            notes=item.notes,
            sort_order=item.sort_order
        )
        db.session.add(new_item)

    db.session.commit()
    return new_bom


def refresh_all_prices(bom: BillOfMaterials) -> Dict[str, Any]:
    updated_count = 0
    price_changes = []

    for item in bom.items:
        if item.material:
            old_price = item.unit_price_snapshot
            new_price = item.material.price
            if old_price != new_price:
                price_changes.append({
                    'material_id': item.material_id,
                    'material_name': item.material.name,
                    'old_price': old_price,
                    'new_price': new_price,
                    'quantity': item.quantity,
                    'old_line_total': item.quantity * (old_price or 0),
                    'new_line_total': item.quantity * new_price
                })
                item.unit_price_snapshot = new_price
                updated_count += 1

    db.session.commit()

    return {
        'updated_count': updated_count,
        'price_changes': price_changes,
        'new_total': bom.total_cost
    }


def export_bom_to_csv(bom: BillOfMaterials) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Item #', 'Material Name', 'Category', 'Supplier',
        'Quantity', 'Unit', 'Unit Price', 'Line Total', 'Notes'
    ])

    for idx, item in enumerate(bom.items.order_by(BOMItem.sort_order), 1):
        material = item.material
        writer.writerow([
            idx,
            material.name if material else 'Unknown',
            material.category if material else '',
            material.supplier.name if material and material.supplier else '',
            item.quantity,
            material.unit if material else '',
            f"${item.unit_price_snapshot:.2f}" if item.unit_price_snapshot else '',
            f"${item.line_total:.2f}",
            item.notes or ''
        ])

    writer.writerow([])
    writer.writerow(['', '', '', '', '', '', 'TOTAL:', f"${bom.total_cost:.2f}", ''])

    return output.getvalue()


def get_bom_summary(bom: BillOfMaterials) -> Dict[str, Any]:
    items = list(bom.items)

    category_totals = {}
    supplier_totals = {}

    for item in items:
        if item.material:
            category = item.material.category or 'Uncategorized'
            category_totals[category] = category_totals.get(category, 0) + item.line_total

            if item.material.supplier:
                supplier = item.material.supplier.name
                supplier_totals[supplier] = supplier_totals.get(supplier, 0) + item.line_total

    return {
        'total_cost': bom.total_cost,
        'item_count': len(items),
        'unique_materials': len(set(item.material_id for item in items)),
        'by_category': [
            {'category': k, 'total': v}
            for k, v in sorted(category_totals.items(), key=lambda x: -x[1])
        ],
        'by_supplier': [
            {'supplier': k, 'total': v}
            for k, v in sorted(supplier_totals.items(), key=lambda x: -x[1])
        ]
    }


def reorder_items(bom_id: int, item_order: List[int]) -> bool:
    for idx, item_id in enumerate(item_order):
        item = BOMItem.query.filter_by(id=item_id, bom_id=bom_id).first()
        if item:
            item.sort_order = idx
    db.session.commit()
    return True
