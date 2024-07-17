
from flask import flash
from app.utils import getCursor, closeCursorAndConnection
from collections import namedtuple
from datetime import date


class Session():
	tableName = 'therapeutic'

	def getSessionsByTherapistId(id):
		cursor, connection = getCursor()
		query = (f"""
		SELECT {Session.tableName}.*,
			session.type as type, session.description as description,
			fees.fees_name as fees_name, fees.price as price,
			room.room_name as room_name,
			CONCAT(userrole.first_name, ' ', userrole.last_name) AS therapist_name
			FROM {Session.tableName}
			JOIN userrole ON {Session.tableName}.therapist_id = userrole.userID
			JOIN session ON {Session.tableName}.type_id = session.type_id
			JOIN fees ON {Session.tableName}.fees_id = fees.fees_id
			JOIN room ON {Session.tableName}.room_id = room.room_id
			WHERE {Session.tableName}.date >= CURDATE()
		""")
		if id != None:
			query += f"AND {Session.tableName}.therapist_id = %s ORDER BY {Session.tableName}.is_available DESC, {Session.tableName}.date ASC"
			cursor.execute(query, (id,))
		else:
			query += f"ORDER BY {Session.tableName}.is_available DESC, {Session.tableName}.date ASC"
			cursor.execute(query)
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description]) # create a namedtuple from the cursor description
		sessions = list(map(lambda row: Row(*row), rows)) # map the rows to the namedtuple
		closeCursorAndConnection()
		return sessions 
	
	def getSessionByTherapeuticId(therapeutic_id):
		cursor, connection = getCursor()
		query = (f"""
			SELECT {Session.tableName}.*,
				session.type as type, session.description as description,
				fees.fees_name as fees_name, fees.price as price,
				room.room_name as room_name
				FROM {Session.tableName}
				JOIN session ON {Session.tableName}.type_id = session.type_id
				JOIN fees ON {Session.tableName}.fees_id = fees.fees_id
				JOIN room ON {Session.tableName}.room_id = room.room_id
				WHERE {Session.tableName}.therapeutic_id = %s
			""")
		cursor.execute(query, (therapeutic_id,))
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		session = Row(*rows[0]) if rows else None
		closeCursorAndConnection()
		return session

	def changeTherapeuticAvailability(cursor, therapeuticId, isAvailable):
		try:
			query = f"UPDATE therapeutic SET is_available = %s WHERE therapeutic_id = %s"
			cursor.execute(query, (isAvailable, therapeuticId))
		except Exception as e:
			print(f"error in chage availability")
			raise Exception(e)
	
	def insertBooking(cursor, memberId, therapeuticId, paymentId):
		try:
			query = f"INSERT INTO therapeutic_booking (member_id, therapeutic_id, payment_id) VALUES (%s, %s, %s)"
			cursor.execute(query, (memberId, therapeuticId, paymentId))
		except Exception as e:
			print(f"error in insert booking")
			raise Exception(e)
	
	def addAttendance(cursor, memberId, bookingId):
		try:
			query = f"""
				INSERT INTO therapeutic_attendance_record (therapeutic_booking_id, member_id, is_attended)
				VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE is_attended = 1
			""" 
			cursor.execute(query, (bookingId, memberId))
		except Exception as e:
			print(f"error in add attendance")
			raise Exception(e)
		
	def addTransaction(cursor, memberId, feesId, amount):
		try:
			query = f"INSERT INTO payment_transaction (member_id, fees_id, payment_date, amount) VALUES (%s, %s, %s, %s)" 
			cursor.execute(query, (memberId, feesId, date.today(), amount))
		except Exception as e:
			print(f"error in add transaction")
			raise Exception(e)

	def bookSessionById(userId, therapeuticId, feesId, amount):
		cursor, connection = getCursor()
		try:
			Session.addTransaction(cursor, userId, feesId, amount)
			paymentId = cursor.lastrowid
			Session.insertBooking(cursor, userId, therapeuticId, paymentId)
			bookingId = cursor.lastrowid
			Session.changeTherapeuticAvailability(cursor, therapeuticId, 0)
			Session.addAttendance(cursor, userId, bookingId)
			connection.commit()
		except Exception as e:
				connection.rollback()
				print(f"error: {e} in booking")
				flash(f"Error: {e}. Booking failed. Please try again.", "danger")
				return False
		finally:
			closeCursorAndConnection()
		return True
	
	def getAllBookingsbyID(id):
		cursor, connection = getCursor()
		query = """
			SELECT * FROM (
				SELECT 
					'class' AS booking_type,
					class_booking.class_booking_id AS booking_id,
					class_booking.date AS date,
					class_booking.class_id AS event_id,
					class_info.type AS event_type,
					class.start_time,
					class.end_time,
					class.duration,
					room.room_name AS location
				FROM `class_booking`
				JOIN 
					class ON class_booking.class_id = class.class_id
				JOIN 
					class_info ON class.type_id = class_info.type_id
				JOIN 
					room ON class.room_id = room.room_id
				WHERE class_booking.member_id = %s

				UNION ALL

				SELECT 
					'therapeutic' AS booking_type,
					therapeutic_booking.therapeutic_booking_id AS booking_id,
					therapeutic.date AS date,
					therapeutic.therapeutic_id AS event_id,
					session.type AS event_type,
					therapeutic.start_time,
					therapeutic.end_time,
					therapeutic.duration,
					room.room_name AS location
				FROM `therapeutic_booking`
				JOIN 
					therapeutic ON therapeutic_booking.therapeutic_id = therapeutic.therapeutic_id
				JOIN 
					session ON therapeutic.type_id = session.type_id
				JOIN 
					room  ON therapeutic.room_id = room.room_id
				WHERE therapeutic_booking.member_id = %s
			) AS bookings
			ORDER BY date ASC;
		"""
		cursor.execute(query, (id, id,))
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		bookings = [Row(*row)._asdict() for row in rows]
		closeCursorAndConnection()
		return bookings
	
	def cancelClassBooking(bookingId):
		cursor, connection = getCursor()
		query = "DELETE FROM class_booking WHERE class_booking_id = %s"
		cursor.execute(query, (bookingId,))
		connection.commit()
		closeCursorAndConnection()

	def deleteTherapeuticBooking(cursor, bookingId):
		cursor.execute("""SELECT p.payment_id
						  FROM payment_transaction p
						  JOIN therapeutic_booking t ON t.payment_id = p.payment_id
						  WHERE t.therapeutic_booking_id = %s""", (bookingId,))
		paymentId = cursor.fetchone()[0]
		try:
			query = "DELETE FROM payment_transaction WHERE payment_id = %s"
			cursor.execute(query, (paymentId,))
		except Exception as e:
			print(f"error in delete booking")
			raise Exception(e)
		
	def cancelTherapeuticBooking(bookingId, therapeuticId):
		cursor, connection = getCursor()
		try:
			Session.deleteTherapeuticBooking(cursor, bookingId)
			Session.changeTherapeuticAvailability(cursor, therapeuticId, 1)
			connection.commit()
		except Exception as e:
				connection.rollback()
				print(f"error: {e}")
				flash(f"Error: {e}. Cancal Booking failed. Please try again.", "danger")
				return False
		finally:
			closeCursorAndConnection()
		return True
	
	