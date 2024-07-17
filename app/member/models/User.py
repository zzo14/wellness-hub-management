from flask import flash
from app.utils import getCursor, closeCursorAndConnection
from collections import namedtuple
from datetime import datetime


class User():
	tableName = 'userrole'

	def getUserById(id):
		cursor, connection = getCursor()
		query = (f"SELECT * FROM {User.tableName} WHERE userID = %s")
		cursor.execute(query, (id,))
		row = cursor.fetchone()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		user = Row(*row)
		closeCursorAndConnection()
		return user 
	
	def getUsersByRole(role):
		cursor, connection = getCursor()
		query = (f"SELECT * FROM {User.tableName} WHERE role = %s AND is_active = 1")
		cursor.execute(query, (role,))
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		users = list(map(lambda row: Row(*row), rows))
		closeCursorAndConnection()
		return users

	def updateUser(userId, user):
		cursor, connection = getCursor()
		fields = map(lambda field: field + " = %s", user.keys())
		fieldsString = ', '.join(fields)
		query = f"UPDATE userrole SET {fieldsString} WHERE userID = %s"
		params = list(user.values())
		params.append(userId)
		try:
			cursor.execute(query, params)
			connection.commit()
		except Exception as e:
				connection.rollback()
				print(f"error: {e}")
				flash(f"Error: {e}. Update failed. Please try again.", "danger")
				return False
		finally:
			closeCursorAndConnection()
		return True if cursor.rowcount > 0 else False
	
	def getSessionsByTherapist(therapist_id):
		cursor, connection = getCursor()
		query = """
			SELECT session.* FROM `session` 
				JOIN therapeutic ON session.`type_id` = therapeutic.`type_id`
				JOIN userrole ON userrole.`userID` = therapeutic.`therapist_id`
				WHERE userrole.`userID` = %s;
		"""
		cursor.execute(query, (therapist_id,))
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		sessions = list(map(lambda row: Row(*row), rows))
		closeCursorAndConnection()
		return sessions
	
	def getMembershipDetailById(member_id):
		cursor, connection = getCursor()
		query = """
			SELECT * FROM `membership` 
				WHERE member_id = %s;
		"""
		cursor.execute(query, (member_id,))
		row = cursor.fetchone()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		membership = Row(*row)
		closeCursorAndConnection()
		return membership
	
	def getMembershipPaymentsById(member_id):
		cursor, connection = getCursor()
		query = """
			SELECT
				payment_transaction.*,
				fees.fees_name as fees_name,
				fees.price as price,
				payment_type.description as payment_type
				FROM `payment_transaction` 
				JOIN fees ON fees.fees_id = payment_transaction.fees_id
				JOIN payment_type ON payment_type.payment_type_id = fees.payment_type_id
				WHERE payment_transaction.member_id = %s
				ORDER BY payment_transaction.payment_date DESC;
		"""
		cursor.execute(query, (member_id,))
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		membershipPayments = list(map(lambda row: Row(*row), rows))
		closeCursorAndConnection()
		return membershipPayments

	def getClassBookings():
		cursor, connection = getCursor()
		query = """
			SELECT 
        	cb.class_booking_id AS booking_id,
        	cb.class_id AS event_id,
        	member_id,
        	ci.type AS event_type,
        	c.repeat_days,
        	c.start_time,
        	c.end_time,
        	c.duration,
        	r.room_name AS location,
        	u.username AS therapist,
        	car.is_attended,
        	'class' AS booking_type
    		FROM 
        		class_booking cb
    		JOIN 
        		class c ON cb.class_id = c.class_id
    		JOIN 
        		class_info ci ON c.type_id = ci.type_id
    		JOIN 
        		userrole u ON c.therapist_id = u.userID
    		JOIN 
        		room r ON c.room_id = r.room_id
    		JOIN 
        		class_attendance_record car ON cb.class_booking_id = car.class_booking_id
    	"""
		cursor.execute(query)
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		class_bookings = [Row(*row)._asdict() for row in rows]
		closeCursorAndConnection()
		return class_bookings
	
	def getTherapeuticBookings():
		cursor, connection = getCursor()
		query = """
    		SELECT 
        	tb.therapeutic_booking_id AS booking_id,
        	t.therapeutic_id AS event_id,
        	tb.member_id,
        	s.type AS event_type,
        	NULL AS repeat_days,
        	t.start_time,
        	t.end_time,
        	t.duration,
        	r.room_name AS location,
        	u.username AS therapist,
        	tar.is_attended,
        	'therapeutic' AS booking_type
    		FROM 
        		therapeutic_booking tb
    		JOIN 
        		therapeutic t ON tb.therapeutic_id = t.therapeutic_id
    		JOIN 
        		session s ON t.type_id = s.type_id
    		JOIN 
        		userrole u ON t.therapist_id = u.userID
    		JOIN 
        		room r ON t.room_id = r.room_id
    		JOIN 
        	therapeutic_attendance_record tar ON tb.therapeutic_booking_id = tar.therapeutic_booking_id
    	"""
		cursor.execute(query)
		rows = cursor.fetchall()
		Row = namedtuple("Row", [column[0] for column in cursor.description])
		therapeutic_bookings = [Row(*row)._asdict() for row in rows]
		closeCursorAndConnection()
		return therapeutic_bookings
	
	def cancelClassBooking(booking_id):
		cursor, connection = getCursor()
		query = "DELETE FROM class_booking WHERE class_booking_id = %s"
		cursor.execute(query, (booking_id,))
		connection.commit()
		closeCursorAndConnection()	

	def cancelTherapeuticBooking(booking_id):
		cursor, connection = getCursor()
		query = "DELETE FROM therapeutic_booking WHERE therapeutic_booking_id = %s"
		cursor.execute(query, (booking_id,))
		connection.commit()
		closeCursorAndConnection()
	
	def cancelMembership(member_id):
		cursor, connection = getCursor()
		query = "UPDATE membership SET membership_status = 0, expiry_date = CURDATE() WHERE member_id = %s"
		try:
			cursor.execute(query, (member_id,))
			connection.commit()
		except Exception as e:
				connection.rollback()
				print(f"error: {e}. At cancelMembership")
				flash(f"Error: {e}. Cancel maembership failed. Please try again.", "danger")
				return False
		finally:
			closeCursorAndConnection()
		return True if cursor.rowcount > 0 else False
	
	def refundMembershipPayment(member_id):
		cursor, connection = getCursor()
		query = """SELECT payment_id 
				   FROM membership 
				   WHERE member_id = %s"""
		cursor.execute(query, (member_id,))
		result = cursor.fetchone()
		try:
			if result:
				payment_ids = result[0]
				query = "DELETE FROM payment_transaction WHERE payment_id = %s"
				cursor.execute(query, (payment_ids,))
				connection.commit()
		except Exception as e:
				connection.rollback()
				print(f"error: {e}. At refundMembershipPayment")
				flash(f"Error: {e}. Refund payment failed. Please try again.", "danger")
		finally:
			closeCursorAndConnection()
		return True if cursor.rowcount > 0 else False
