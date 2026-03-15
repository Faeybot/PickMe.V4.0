from sqlalchemy import select, and_
from models import User
from database import async_session
from geopy.distance import geodesic

class DatingService:
    @staticmethod
    async def get_nearby_users(user_id, gender_pref, u_lat, u_lon):
        async with async_session() as session:
            # Mencari user dengan gender yang diinginkan dan tidak diblokir
            stmt = select(User).where(
                and_(
                    User.gender == gender_pref, 
                    User.id != user_id, 
                    User.is_banned == False
                )
            )
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            # Menghitung jarak menggunakan Geopy
            scored = []
            for u in users:
                dist = geodesic((u_lat, u_lon), (u.latitude, u.longitude)).km
                scored.append((u, dist))
            
            # Mengurutkan dari yang paling dekat
            scored.sort(key=lambda x: x[1])
            return scored[0] if scored else None
