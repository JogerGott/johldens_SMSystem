from sqlalchemy.orm import Session
from src.models import Box, BoxStatus, BoxStateColor

class BoxRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_box(self, color: str, number: int) -> Box:
        box_color = BoxStateColor(color.lower())
        new_box = Box(color=box_color, number=number, status=BoxStatus.LIBRE)
        self.session.add(new_box)
        self.session.commit()
        self.session.refresh(new_box)
        return new_box

    def check_box(self, id_box: int) -> Box:
        return self.session.query(Box).filter(Box.id_box == id_box).first()

    def list_available_box(self):
        return self.session.query(Box).filter(Box.status == BoxStatus.LIBRE).all()

    def list_available_box_by_color(self, color: str):
        box_color = BoxStateColor(color.lower())
        return self.session.query(Box).filter(Box.status == BoxStatus.LIBRE, Box.color == box_color).all()

    def change_box_status(self, id_box: int, status: str) -> Box:
        box = self.check_box(id_box)
        if box:
            new_status = BoxStatus(status.upper())
            box.status = new_status
            self.session.commit()
            self.session.refresh(box)
        return box
