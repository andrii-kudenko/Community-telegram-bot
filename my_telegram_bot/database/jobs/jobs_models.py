# from ..models import Base
# from sqlalchemy import Integer, String, ForeignKey, BigInteger, Boolean
# from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship


# class Job(Base):
#     __tablename__ = 'jobs'

#     id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
#     user_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.user_id'), unique=True, nullable=False, index=True) 
#     title: Mapped[str] = mapped_column(String(30), nullable=False)
#     description: Mapped[str] = mapped_column(String(255), nullable=False)
#     skills: Mapped[str] = mapped_column(String(255), nullable=False)  # Store skills as a comma-separated string
#     # location = mapped_column(String, nullable=False)
#     latitude: Mapped[str] = mapped_column(String(15))
#     longtitude: Mapped[str] = mapped_column(String(15))
#     city: Mapped[str] = mapped_column(String(40))
#     address: Mapped[str] = mapped_column(String(40))
#     user = relationship("User", back_populates="job")

#     def get_skills(self):
#         return self.skills.split(",")  # Convert comma-separated string back to list