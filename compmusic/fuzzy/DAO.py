# -*- coding: utf-8 -*-
import MySQLdb
import datetime
import types

class DAO:
	def __init__(self):
		self.database = "compmusic" 
		self.user = "compmusic"
		self.host = "localhost"
		self.passwd = "compmusic123"
	def connection(self):
		# Connect to the DB
		#print "Connecting to DB"
		try:
			conn = MySQLdb.connect(db=self.database, user=self.user, host=self.host, passwd = self.passwd)
		except MySQLdb.OperationalError, msg:
			print "Cannot connect to the database: %s" % unicode(msg)
			return False
		return conn
		
	def getCollections(self):
		# get the current replication number
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			curs.execute("SELECT `mbid`, `name` FROM `collection` WHERE 1")
			rows = curs.fetchall()
			if len(rows) > 0:
				drows = []
				for row in rows:
					drow = {"mbid": row[0], 
						"name": row[1], 
					}
					drows.append(drow)
				data = (True, drows[:], "")
			else:
				data = (False, "empty", "")
			conn.close()
		return data
	
	def getCollectionInfo(self, attr_name, attr_value):
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				curs.execute("SELECT `mbid`, `name` FROM `collection` WHERE %s='%s'" % (attr_name, attr_value))
				rows = curs.fetchall()
				if len(rows) > 0:
					drow = {"mbid": rows[0][0], 
						"name": rows[0][1], 
					}
					data = (True, drow, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getRelations(self, attr_name, attr_value, table='recording', collection=None):
		"""
		Returns relations which match the given criteria. The criteria can be either
		'type' or 'attribute' from the relation table. For example,
		getRelations('type', 'instrument') fetches all the recording relations where an 
		instrument is involved, or getRelations('type', 'composer') fetches 
		all the work relations where a composer is involved..
		Whereas getRelations('attribute', 'ghatam') 
		fetches the relations where "ghatam" is involved.
		"""
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT rel.uuid_entity1, rel.uuid_entity2,
					rel.type, rel.attribute
					FROM `relation` rel, `%s` t, `collection` c
					WHERE (rel.uuid_entity1 = t.uuid OR rel.uuid_entity2 = t.uuid)
					AND c.mbid = t.collection_mbid
					%s
					AND rel.%s='%s'""" % (table, str_collection, attr_name, attr_value)
				print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid1": row[0],
							"uuid2": row[1],
							"type": row[2],
							"attribute": row[3],
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getDistinctRelations(self, attr_name, attr_value, table='recording', collection=None):
		"""
		Returns relations which match the given criteria. The criteria can be either
		'type' or 'attribute' from the relation table. For example,
		getRelations('type', 'instrument') fetches all the recording relations where an 
		instrument is involved, or getRelations('type', 'composer') fetches 
		all the work relations where a composer is involved..
		Whereas getRelations('attribute', 'ghatam') 
		fetches the relations where "ghatam" is involved.
		"""
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT rel.attribute
					FROM `relation` rel, `%s` t, `collection` c
					WHERE (rel.uuid_entity1 = t.uuid OR rel.uuid_entity2 = t.uuid)
					AND c.mbid = t.collection_mbid
					%s
					AND rel.%s='%s'""" % (table, str_collection, attr_name, attr_value)
				print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {
							"type": row[0],
							"attribute": row[1],
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	
	def getArtists(self, rel_table="recording", collection=None):
		#TODO artists' names and aliases --> unicode
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT a.uuid, a.name, c.name
				FROM `artist` a, `%s` rt, `collection` c
				WHERE rt.artist_uuid = a.uuid 
				%s
				AND a.collection_mbid = c.mbid""" % (rel_table, str_collection)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"name": row[1], 
							"collection": {"name": row[2]},
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getArtistsRecordings(self, collection=None):
		#TODO artists' names and aliases --> unicode
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT a.uuid, a.name, r.uuid, r.title, c.name
				FROM `artist` a, `recording` r, `collection` c
				WHERE r.artist_uuid = a.uuid 
				%s
				AND a.collection_mbid = c.mbid""" % (str_collection)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"name": row[1], 
							"recording": {"uuid": row[2], "title": row[3]},
							"collection": {"name": row[4]},
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	#def getArtistsByTagCategory(self, ):
		#pass
	
	#def getArtistsByTag(self, ):
		#pass
	
	#def 
	
	def getArtistInfo(self, attr_name, attr_value):
		#TODO artists' names and aliases --> unicode
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT a.uuid, a.name, a.type, a.alias, a.gender, a.country, a.birthdate
				FROM `artist` a
				WHERE %s='%s'""" % (attr_name, attr_value)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drow = {"uuid": rows[0][0], 
						"name": rows[0][1], 
						"type": rows[0][2], 
						"aliases": [] if not rows[0][3] else rows[0][3].split(";"),
						"gender": rows[0][4],
						"country": rows[0][5],
						"birthdate": "unknown" if rows[0][6] == None else rows[0][6].isoformat(),
					}
					data = (True, drow, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getArtistsRelation(self, attr_name, attr_value, rel_table='recording', relation=None):
		"""
		Get all the artists related to a relation table. For example, getArtistsRelation('uuid', 'xxxx', rel_table='recording')
		will return all the artists related to the recording with uuid=xxxx
		"""
		conn = self.connection()
		data = (False, "connection", "")
		str_relation = ""
		if relation:
			str_relation = "AND rel.type = '%s'" % relation
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT a.uuid, a.name, rel.type, rel.attribute
				FROM `artist` a, `relation` rel, `%s` rt
				WHERE rt.%s='%s'
				AND (rel.uuid_entity1 = a.uuid AND rt.uuid = rel.uuid_entity2 OR 
					rel.uuid_entity1 = rt.uuid AND a.uuid = rel.uuid_entity2)
				%s""" % (rel_table, attr_name, attr_value, str_relation)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"name": row[1], 
							"relation": { "type": row[2], "attribute": row[3]},
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getArtistRelations(self, attr_name, attr_value, rel_table='recording', relation=None):
		"""
		Get all the relations where artist is involved. For example, getArtistRelations('name', 'Bajeddoub & Souiri', rel_table='recording')
		will return all the recordings where the duo Bajeddoub & Souiri is involved
		"""
		conn = self.connection()
		data = (False, "connection", "")
		str_relation = ""
		if relation:
			str_relation = "AND rel.type = '%s'" % relation
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT a.uuid, a.name, rt.uuid, rt.title, rel.type, rel.attribute
				FROM `artist` a, `relation` rel, `%s` rt
				WHERE a.%s='%s'
				AND (rel.uuid_entity1 = a.uuid AND rt.uuid = rel.uuid_entity2 OR 
					rel.uuid_entity1 = rt.uuid AND a.uuid = rel.uuid_entity2)
				%s""" % (rel_table, attr_name, attr_value, str_relation)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"name": row[1], 
							"relation": { "uuid": row[2], "title": row[3], "type": row[4], "attribute": row[5]},
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getArtistsRelations(self, rel_table='recording', relation=None, collection=None):
		"""
		Get all artists and their involvement in the specified relations. For example, 
		getArtistsRelations(rel_table='recording', relation=['instrument', 'vocal']) will return all the artists that 
		played an instrument or sung vocals in recordings
		"""
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		str_relation = "WHERE"
		if type(relation) is types.StringType:
			str_relation = "WHERE rel.type IN ('%s') AND" % relation
		elif type(relation) is types.ListType or type(relation) is types.TupleType:
			relations = str(['%s' % r for r in relation])
			str_relation = "WHERE rel.type IN %s AND" % relations.replace("[", "(").replace("]", ")")
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT a.uuid, a.name, rt.uuid, rt.title, rel.type, rel.attribute, c.name
				FROM `artist` a, `relation` rel, `%s` rt, `collection` c
				%s 
				( a.uuid = rel.uuid_entity1 AND rt.uuid = rel.uuid_entity2)
				AND a.collection_mbid = c.mbid
				%s
				""" % (rel_table, str_relation, str_collection)
				print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"name": row[1],
							"relation": { "uuid": row[2], "title": row[3], "type": row[4], "attribute": row[5]},
							"collection": {"name": row[6]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getArtistRelationsAttribute(self, attr_name, attr_value, rel_table='recording', relation=None):
		"""
		Get the relation attributes where artist is involved. For example, getArtistRelations('name', 'Karaikudi Mani', rel_table='recording', relation="instrument")
		will return all the instruments that artist Karaikudi Mani plays
		"""
		conn = self.connection()
		data = (False, "connection", "")
		str_relation = ""
		if relation:
			str_relation = "AND rel.type = '%s'" % relation
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT rel.type, rel.attribute
				FROM `artist` a, `relation` rel, `%s` rt
				WHERE a.%s='%s'
				AND (rel.uuid_entity1 = a.uuid AND rt.uuid = rel.uuid_entity2 OR 
					rel.uuid_entity1 = rt.uuid AND a.uuid = rel.uuid_entity2)
				%s""" % (rel_table, attr_name, attr_value, str_relation)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"type": row[0], "attribute": row[1]
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getWorkRelationByRecording(self, attr_name, attr_value, relation=None):
		conn = self.connection()
		data = (False, "connection", "")
		str_relation = ""
		if relation:
			str_relation = "AND rel.type = '%s'" % relation
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT w.uuid, w.title, rel.type, rel.attribute
				FROM `work` w, `relation` rel, `recording` r
				WHERE r.%s='%s'
				AND (rel.uuid_entity1 = w.uuid AND r.uuid = rel.uuid_entity2 OR 
					rel.uuid_entity1 = r.uuid AND w.uuid = rel.uuid_entity2)
				%s
				""" % (attr_name, attr_value, str_relation)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drow = {"uuid": rows[0][0], 
						"title": rows[0][1], 
						"relation": { "type": rows[0][2], "attribute": rows[0][3]},
					}
					data = (True, drow, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getWorks(self, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT w.uuid, w.title, a.uuid, a.name, rel.type, c.name
					FROM `work` w, `artist` a, `relation` rel, `collection` c
					WHERE (rel.type = 'composer' OR rel.type = 'lyricist')
					AND ( a.uuid = rel.uuid_entity1 AND w.uuid = rel.uuid_entity2)
					AND w.collection_mbid = c.mbid
					%s""" % (str_collection)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = {}
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1],
							"artists": [{"uuid": row[2], "name": row[3].encode("utf-8"), "relation": row[4]}],
							"collection": {"name": row[5]}
						}
						print drow["artists"]
						if not drows.has_key(drow["uuid"]):
							drows[drow["uuid"]] = drow
						else:
							drows[drow["uuid"]]["artists"].extend(drow["artists"])
					data = (True, drows.values(), "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getWorkInfo(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT w.uuid, w.title, c.name
					FROM `work` w, `collection` c
					WHERE w.%s='%s' 
					AND c.mbid = w.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drow = {"uuid": rows[0][0], 
						"title": rows[0][1],
						"collection": {"name": rows[0][2]}
					}
					data = (True, drow, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getReleases(self, collection=None, limit=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		str_limit = ""
		if limit:
			str_limit = "LIMIT %d" % int(limit)
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			query = """SELECT DISTINCT rl.uuid, rl.title
				FROM `release` rl, `collection` c
				WHERE rl.collection_mbid = c.mbid %s
				%s """ % (str_collection, str_limit)
			curs.execute(query.encode("utf-8"))
			rows = curs.fetchall()
			if len(rows) > 0:
				drows = []
				for row in rows:
					drow = { 
						"uuid": row[0],
						"title": row[1]
					}
					drows.append(drow)
				data = (True, drows[:], "")
			else:
				data = (False, "empty", "")
			conn.close()
		return data
		
	def getRelease(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT rl.uuid, rl.title, rl.status, rl.date, a.uuid, a.name, c.name
					FROM `release` rl, `artist` a, `collection` c
					WHERE rl.%s='%s' 
					AND  a.uuid = rl.artist_uuid
					AND c.mbid = rl.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drow = {"uuid": rows[0][0], 
						"title": rows[0][1],
						"status": rows[0][2], 
						"date": rows[0][3],
						"artist": {"uuid": rows[0][4], "name": rows[0][5]},
						"collection": {"name": rows[0][6]}
					}
					data = (True, drow, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	
	def getReleasesByArtist(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT rl.uuid, rl.title, a.uuid, a.name, c.name
					FROM `release` rl, `artist` a, `collection` c
					WHERE a.%s='%s' 
					AND rl.artist_uuid = a.uuid
					AND c.mbid = rl.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"artist": {"uuid": row[2], "name": row[3]},
							"collection": {"name": row[4]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getReleasesByArtistRelation(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT rl.uuid, rl.title, a.uuid, a.name, rel.type, rel.attribute, c.name
					FROM `release` rl, `artist` a, `relation` rel, `collection` c
					WHERE a.%s='%s' 
					AND (rel.uuid_entity1 = a.uuid AND rl.uuid = rel.uuid_entity2 OR 
						rel.uuid_entity1 = rl.uuid AND a.uuid = rel.uuid_entity2) 
					AND c.mbid = rl.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"artist": {"uuid": row[2], "name": row[3], "relation": {"type": row[4],
							"attribute": row[5]}},
							"collection": {"name": row[6]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getRecordings(self, uuid=None, collection=None, limit=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		str_limit = ""
		if limit:
			str_limit = "LIMIT %d" % int(limit)
		str_uuid = "WHERE"
		if uuid:
			str_uuid = "WHERE r.uuid='%s' AND" % uuid
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, r.length, a.uuid, a.name, rl.uuid, rl.title, c.name
					FROM `recording` r, `artist` a, `release` rl, `collection` c
					%s r.collection_mbid = c.mbid
					AND a.uuid = r.artist_uuid
					AND rl.uuid = r.release_uuid
					%s
					%s """ % (str_uuid, str_collection, str_limit)
				print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = { 
							"uuid": row[0], 
							"title": row[1], 
							"length": int(row[2]),
							"artist": {"uuid": row[3], "name": row[4]},
							"release": {"uuid": row[5], "title": row[6]},
							"collection": {"name": row[7]}
						}
						drows.append(drow)
					data = (True, drows[:], "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getRecording(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, r.length, a.uuid, a.name, rl.uuid, rl.title, c.name
					FROM `recording` r, `artist` a, `release` rl, `collection` c
					WHERE r.%s='%s' 
					AND  a.uuid = r.artist_uuid
					AND rl.uuid = r.release_uuid
					AND c.mbid = r.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drow = {"uuid": rows[0][0], 
						"title": rows[0][1], 
						"length": int(rows[0][2]),
						"artist": {"uuid": rows[0][3], "name": rows[0][4]},
						"release": {"uuid": rows[0][5], "title": rows[0][6]},
						"collection": {"name": rows[0][7]}
					}
					data = (True, drow, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getRecordingsByTag(self, attr_name, tag, category='unknown', collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			query = """SELECT r.uuid, r.title, r.length, a.uuid, a.name, t.tag, t.category, rl.uuid, rl.title, c.name
				FROM `recording` r, `artist` a, `annotation` ann, `tag` t, `release` rl, `collection` c
				WHERE t.%s = '%s'
				AND t.category LIKE '%s%%'
				AND ann.tag_id = t.id
				AND r.uuid = ann.uuid_entity 
				AND a.uuid = r.artist_uuid
				AND rl.uuid = r.release_uuid
				AND c.mbid = a.collection_mbid
				%s""" % (attr_name, tag, category, str_collection)
			curs.execute(query.encode("utf-8"))
			rows = curs.fetchall()
			if len(rows) > 0:
				drows = []
				for row in rows:
					drow = {"uuid": row[0], 
						"title": row[1], 
						"length": int(row[2]),
						"artist": {"uuid": row[3], "name": row[4]},
						"tag": {"name": row[5], "category": row[6]},
						"release": {"uuid": row[7], "title": row[8]},
						"collection": {"name": row[9]}
					}
					drows.append(drow)
				data = (True, drows[:], "")
			else:
				data = (False, [], "")
			conn.close()
		return data
	
	def getRecordingsByArtist(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, a.uuid, a.name, rl.uuid, rl.title, c.name
					FROM `recording` r, `artist` a, `release` rl, `collection` c
					WHERE a.%s='%s' 
					AND r.artist_uuid = a.uuid
					AND rl.uuid = r.release_uuid
					AND c.mbid = r.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"artist": {"uuid": row[2], "name": row[3]},
							"release": {"uuid": row[4], "title": row[5]},
							"collection": {"name": row[6]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getRecordingsByArtistRelation(self, attr_name, attr_value, collection=None):
		#TODO relate also with releases
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, a.uuid, a.name, rl.uuid, rl.title, rel.type, rel.attribute, c.name
					FROM `recording` r, `artist` a, `release` rl, `relation` rel, `collection` c
					WHERE a.%s='%s' 
					AND (rel.uuid_entity1 = a.uuid AND r.uuid = rel.uuid_entity2 OR 
						rel.uuid_entity1 = r.uuid AND a.uuid = rel.uuid_entity2) 
					AND rl.uuid = r.release_uuid
					AND c.mbid = r.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"artist": {"uuid": row[2], "name": row[3], "relation": {"type": row[6],
							"attribute": row[7]}},
							"release": {"uuid": row[4], "title": row[5]},
							"collection": {"name": row[8]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
	
	def getRecordingsByRelease(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, r.length, a.uuid, a.name, rl.uuid, rl.title, c.name
					FROM `recording` r, `artist` a, `release` rl, `collection` c
					WHERE rl.%s='%s'
					AND r.release_uuid = rl.uuid
					AND a.uuid = rl.artist_uuid
					AND c.mbid = r.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"length": row[2],
							"artist": {"uuid": row[3], "name": row[4]},
							"release": {"uuid": row[5], "title": row[6]},
							"collection": {"name": row[7]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		

	def getRecordingsByWork(self, attr_name, attr_value, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, a.uuid, a.name, rl.uuid, rl.title, w.uuid, w.title, c.name
					FROM `recording` r, `artist` a, `release` rl, `work` w, `relation` rel, `collection` c
					WHERE w.%s='%s'
					AND (rel.uuid_entity1 = w.uuid AND r.uuid = rel.uuid_entity2 OR 
						rel.uuid_entity1 = r.uuid AND w.uuid = rel.uuid_entity2) 
					AND r.release_uuid = rl.uuid
					AND a.uuid = r.artist_uuid
					AND c.mbid = r.collection_mbid
					%s""" % (attr_name, attr_value, str_collection)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"artist": {"uuid": row[2], "name": row[3]},
							"release": {"uuid": row[4], "title": row[5]},
							"work": {"uuid": row[6], "title": row[7]},
							"collection": {"name": row[8]}
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	
		
	def __getRecordingsByInstrument(self, instrument, collection=None):
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			try:
				query = """SELECT DISTINCT r.uuid, r.title, r.length, a.uuid, a.name, rl.uuid, rl.title, rel.attribute, c.name
					FROM `recording` r, `release` rl, `artist` a, `relation` rel, `collection` c
					WHERE rel.type='instrument' AND rel.attribute='%s'
					AND ( r.uuid = rel.uuid_entity2 OR r.uuid = rel.uuid_entity1 ) 
					AND a.uuid = r.artist_uuid
					AND rl.uuid = r.release_uuid
					AND c.mbid = r.collection_mbid
					%s""" % (instrument, str_collection)
				#print query
				curs.execute(query.encode("utf-8"))
				rows = curs.fetchall()
				if len(rows) > 0:
					drows = []
					for row in rows:
						drow = {"uuid": row[0], 
							"title": row[1], 
							"length": row[2], 
							"artist": {"uuid": row[3], "name": row[4]},
							"release": {"uuid": row[5], "title": row[6]},
							"instrument": {"name": row[7]},
							"collection": {"name": row[8]},
						}
						drows.append(drow)
					data = (True, drows, "")
				else:
					data = (False, "empty", "")
			except MySQLdb.OperationalError, msg:
				data = (False, "query", msg)
			conn.close()
		return data
		
	def getRecordingsByInstrument(self, instrument, collection=None):
		data = self.__getRecordingsByInstrument(instrument, collection)
		if data[0] == False:
			return data
		return data
		
	
	def getInstruments(self, collection=None):
		#TODO: relation uuid_entity1 is supposed to be artist uuid
		str_collection = ""
		if collection:
			str_collection = "AND c.name = '%s'" % collection
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			query = """SELECT DISTINCT rel.attribute 
				FROM `relation` rel, `artist` a, `collection` c
				WHERE rel.type='instrument' 
				AND a.uuid = rel.uuid_entity1 
				AND a.collection_mbid = c.mbid %s
				ORDER BY `attribute`""" % (str_collection)
			curs.execute(query.encode("utf-8"))
			rows = curs.fetchall()
			if len(rows) > 0:
				drows = []
				for row in rows:
					drow = { 
						"name": row[0], 
					}
					drows.append(drow)
				data = (True, drows[:], "")
			else:
				data = (False, "empty", "")
			conn.close()
		return data
		
	def getTags(self, uuid):
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			query = """SELECT DISTINCT t.id, t.tag, t.category
				FROM `tag` t, `annotation` ann
				WHERE ann.uuid_entity = '%s'
				AND t.id = ann.tag_id 
				ORDER BY tag""" % (uuid)
			#print query
			curs.execute(query.encode("utf-8"))
			rows = curs.fetchall()
			if len(rows) > 0:
				drows = []
				for row in rows:
					drow = { 
						"id": int(row[0]),
						"tag": row[1],
						"category": row[2]
					}
					drows.append(drow)
				data = (True, drows[:], "")
			else:
				data = (False, "empty", "")
			conn.close()
		return data
	
	def getTagsByCategory(self, category):
		conn = self.connection()
		data = (False, "connection", "")
		if conn:
			curs = conn.cursor()
			query = """SELECT DISTINCT t.id, t.tag, t.category
				FROM `tag` t
				WHERE t.category LIKE '%s%%'
				ORDER BY tag""" % (category)
			#print query
			curs.execute(query.encode("utf-8"))
			rows = curs.fetchall()
			if len(rows) > 0:
				drows = []
				for row in rows:
					drow = { 
						"id": int(row[0]),
						"tag": row[1],
						"category": row[2]
					}
					drows.append(drow)
				data = (True, drows[:], "")
			else:
				data = (False, [], "")
			conn.close()
		return data
	
	# ---------------- HIGHER LEVEL FUNCTIONS --------------------------
	
	#def getComposersInfo(self, collection=None):
		##TODO uuid1 is supposed to be work uuid, whilst uuid2 is artist uuid
		#status, relations, msg = self.getRelations('type', 'composer', table="work", collection=collection)
		#data = (status, relations, msg)
		#composers = {}
		#if status:
			#for relation in relations:
				#if not composers.has_key(relation['uuid2']):
					#composers[relation['uuid2']] = {}
					#status, ainfo, msg = dao.getArtistInfo("uuid", relation['uuid2'])
					#if status:
						#composers[relation['uuid2']] = ainfo
					#composers[relation['uuid2']]["works"] = []
				#status, winfo, msg = self.getWorkInfo("uuid", relation['uuid1'])
				#if status:
					#composers[relation['uuid2']]["works"].append(winfo)
			#data = (True, composers.values(), '')
		#return data
	
	#def getLyricistsInfo(self, collection=None):
		##TODO uuid1 is supposed to be work uuid, whilst uuid2 is artist uuid
		#status, relations, msg = self.getRelations('type', 'lyricist', table="work", collection=collection)
		#data = (status, relations, msg)
		#lyricists = {}
		#if status:
			#for relation in relations:
				#if not lyricists.has_key(relation['uuid2']):
					#lyricists[relation['uuid2']] = {}
					#status, ainfo, msg = dao.getArtistInfo("uuid", relation['uuid2'])
					#if status:
						#lyricists[relation['uuid2']] = ainfo
					#lyricists[relation['uuid2']]["works"] = []
				#status, winfo, msg = self.getWorkInfo("uuid", relation['uuid1'])
				#if status:
					#lyricists[relation['uuid2']]["works"].append(winfo)
				
			#data = (True, lyricists.values(), '')
		#return data
	
	#def getReleasesInfo(self, collection=None, limit=None):
		#status, releases, msg = self.getReleases(collection=collection, limit=limit)
		#data = (status, releases, msg)
		#if status:
			#finalreleases = []
			#for release in releases:
				## get release information
				#status, rinfo, msg = self.getRelease("uuid", release['uuid'])
				#if status:
					#release['artist'] = rinfo['artist']
					#release['collection'] = rinfo['collection']
				##get artist relations: mainly the instrument or vocals
				#status, artistrel, msg = self.getArtistsRelation("uuid", release['uuid'], rel_table="release", relation=None)
				#if status:
					#release['artists'] = [artist for artist in artistrel]
				#finalreleases.append(release)
			#data = (True, finalreleases, '')
		#return data
	
	#def getRecordingsInfo(self, collection=None, limit=None):
		#status, recordings, msg = self.getRecordings(collection=collection, limit=limit)
		#data = (status, recordings, msg)
		#if status:
			#finalrecordings = []
			#for recording in recordings:
				## get recording information
				#status, rinfo, msg = self.getRecording("uuid", recording['uuid'])
				#if status:
					#recording['release'] = rinfo['release']
					#recording['artist'] = rinfo['artist']
					#recording['collection'] = rinfo['collection']
				##get artist relations: mainly the instrument or vocals
				#status, artistrel, msg = self.getArtistsRelation("uuid", recording['uuid'], rel_table="recording", relation=None)
				#if status:
					#recording['artists'] = [artist for artist in artistrel]
				##get work
				#status, work, msg = self.getWorkRelationByRecording("uuid", recording['uuid'], relation=None)
				#if status:
					#recording['work'] = work
					## get work artists: composer, lyricist
					#status, workartist, msg = self.getArtistsRelation("uuid", work['uuid'], rel_table="work", relation=None)
					#if status:
						#recording['work']['artists'] = workartist
				#finalrecordings.append(recording)
			#data = (True, finalrecordings, '')
		#return data
		
	def getRecordingInfo(self, attr_name, attr_value):
		# get recording information
		status, recording, msg = self.getRecording(attr_name, attr_value)
		if status:
			#get tags:
			status, tags, msg = self.getTags(recording['uuid'])
			if status:
				recording['tags'] = [{'id': tag['id'], 'tag': tag['tag'], 'category': tag['category']} for tag in tags]
			#get artist relations: mainly the instrument or vocals
			status, artistrel, msg = self.getArtistsRelation("uuid", recording['uuid'], rel_table="recording", relation=None)
			if status:
				recording['artists'] = [artist for artist in artistrel]
			#get work
			status, work, msg = self.getWorkRelationByRecording("uuid", recording['uuid'], relation=None)
			if status:
				recording['work'] = work
				# get work artists: composer, finalrelation
				status, workartist, msg = self.getArtistsRelation("uuid", work['uuid'], rel_table="work", relation=None)
				if status:
					recording['work']['artists'] = workartist
		return recording
	
	def getReleaseInfo(self, attr_name, attr_value):
		# get release information
		status, release, msg = self.getRelease(attr_name, attr_value)
		if status:
			#get artist relations: mainly the instrument or vocals
			status, artistrel, msg = self.getArtistsRelation("uuid", release['uuid'], rel_table="release", relation=None)
			if status:
				release['artists'] = [artist for artist in artistrel]
		return release
	
	def __getRelationsByWorkInfo(self, relations):
		finalrelations = {}
		for relation in relations:
			if not finalrelations.has_key(relation['uuid']):
				finalrelations[relation['uuid']] = {}
				status, ainfo, msg = self.getArtistInfo("uuid", relation['uuid'])
				if status:
					finalrelations[relation['uuid']] = ainfo
				finalrelations[relation['uuid']]["works"] = []
			status, winfo, msg = self.getWorkInfo("uuid", relation['relation']['uuid'])
			if status:
				finalrelations[relation['uuid']]["works"].append(winfo)
		return finalrelations.values()
	
	def getWorkRelationsInfo(self, relation, collection=None):
		status, relations, msg = self.getArtistsRelations(rel_table="work", relation=relation, collection=collection) #TODO: ArtistsRelations
		finalrelations = []
		if status:
			finalrelations = self.__getRelationsByWorkInfo(relations)
		return finalrelations
		
	def getWorkRelationInfo(self, relation, attr_name, attr_value):
		status, relations, msg = self.getArtistRelations(attr_name, attr_value, rel_table='work', relation=relation)
		finalrelations = []
		if status:
			finalrelations = self.__getRelationsByWorkInfo(relations)
		return finalrelations

	
def print_recording(recording):
	print 'recording.title: %s' % recording['title']
	print 'artist.name: %s' % recording['artist']['name']
	print 'release.title: %s' % recording['release']['title']
	print 'recording.title: %s' % recording['title']
	if recording.has_key('artists'):
		print 'artists'
		for artist in recording['artists']:
			print "\tartist.name: %s" % artist['name']
			print "\trel.type: %s" % artist['relation']['type']
			if artist['relation']['attribute'] != "unknown":
				print "\trel.attribute: %s" % artist['relation']['attribute']
			print "\t------------------"
	if recording.has_key('work'):
		print 'work'
		print "\twork.title: %s" % recording['work']['title']
		print "\trel.type: %s" % recording['work']['relation']['type']
		if recording['work']['relation']['attribute'] != "unknown":
			print "\trel.attribute: %s" % recording['work']['relation']['attribute']
		if recording['work'].has_key('artists'):
			print '\tartists'
			for artist in recording['work']['artists']:
				print "\t\tartist.name: %s" % artist['name']
				print "\t\trel.type: %s" % artist['relation']['type']
				if artist['relation']['attribute'] != "unknown":
					print "\t\trel.attribute: %s" % artist['relation']['attribute']
				print "\t\t------------------"

	
if __name__ == "__main__":
	dao = DAO()
	print dao.getCollections()
	#print dao.getCollectionBy("name", "Andalusian")
	#print dao.getCollectionInfo("mbid", "5d9b5dc6-507b-4f1a-abc4-fefd14f5e84c")
	#print dao.getArtistInfo("name", "Abderrahim Souiri")
	#print dao.getArtistInfo("name", "L. Subramaniam")
	#print dao.getArtistInfo("uuid", "66f992fb-8cfa-4ea5-b80b-20b1af8b310b") # Sudha Ragunathan
	
	#for artist in dao.getArtistsByCollection("Hindustani")[1]:
		#print artist
	#print dao.getReleasesByArtist("uuid", "6317aeac-c108-4c31-a602-51fedc1558ad") # # direct relationship Bajeddoub & Souiri
	#print dao.getReleasesByArtistRelation("uuid", "6bee594d-05b9-4587-88e3-b71c51a407c3") # lead vocal Abderrahim Souiri
	#print dao.getRecordingsByTag("category", "raga", collection="hindustani")
	#status, recordings, msg = dao.getRecordingsByArtist("uuid", "6317aeac-c108-4c31-a602-51fedc1558ad") # direct relationship Bajeddoub & Souiri
	#for recording in recordings: print recording
	#print "-----------------"
	#status, recordings, msg =  dao.getRecordingsByArtistRelation("uuid", "6bee594d-05b9-4587-88e3-b71c51a407c3") # lead vocal Abderrahim Souiri
	#for recording in recordings: print recording
	
	status, relations, msg = dao.getRelations('type', 'composer', table="work", collection="Carnatic")
	print relations
	for relation in relations:
		print dao.getArtistInfo("uuid", relation['uuid1'])
	
	import sys
	sys.exit()
	#print dao.getRecordingsByRelease("uuid", "82c681e1-49cf-4599-a8d4-ca0b1bbd5daf") # L'art du mawwal
	#print dao.getRecordingsByWork("uuid", "0a4aed14-baea-4a7e-8d40-8be69219dbd2") # Jaawali Praana naathan
	
	#for relation in dao.getArtistsRelationByRecording("uuid", "9b01c16f-0e27-446b-b927-15a912b2f862", relation=None)[1]:
		#print relation
	#print dao.getWorkRelationByRecording("uuid", "9b01c16f-0e27-446b-b927-15a912b2f862", relation=None)
	#print dao.getArtistsRelation("uuid", '02d671b6-c116-4632-bb12-60b53973d803', rel_table='work', relation=None)
	print "---------------------------------------------------------------------------"
	print "-------------------------------- TAMBURA --------------------------------"
	print "---------------------------------------------------------------------------"
	finalrecordings = []
	status, recordings, msg = dao.getRecordingsByInstrument("tambura")
	if status:
		for recording in recordings:
			
			# get recording information
			status, rinfo, msg = dao.getRecording("uuid", recording['uuid'])
			if status:
				recording['release'] = rinfo['release']
				recording['artist'] = rinfo['artist']
			#get artist relations: mainly the instrument
			status, artistrel, msg = dao.getArtistsRelation("uuid", recording['uuid'], rel_table="recording", relation=None)
			if status:
				recording['artists'] = [artist for artist in artistrel]
			#get work
			status, work, msg = dao.getWorkRelationByRecording("uuid", recording['uuid'], relation=None)
			if status:
				recording['work'] = work
				# get work artists: composer, lyricist
				status, workartist, msg = dao.getArtistsRelation("uuid", work['uuid'], rel_table='work', relation=None)
				if status:
					recording['work']['artists'] = workartist
			finalrecordings.append(recording)
	for recording in finalrecordings:
		print "-------------% s -- %s -------------------" % (recording['uuid'], recording['title'])
		print_recording(recording)
		break
		
	print dao.getInstruments()
	print "-----------------------------------"
	#status, relations, msg = dao.getRelations('type', 'lyricist', rel_table="work")
	#print relations[0]['uuid1']
	#for relation in relations:
		#print dao.getArtistInfo("uuid", relation['uuid2'])
	#print len(relations)
	#status, relations, msg = dao.getLyricistsInfo(collection="Ottoman")
	#for relation in relations:
		#if len(relation["works"]) <= 1:
			#print relation
	status, artists, msg = dao.getArtistsRecordings(collection="Carnatic")
	#for artist in artists:
		#print artist
	print len(artists)
	#status, artists, msg = dao.getArtistsRelations(rel_table='recording', relation=['vocal', 'collaboration', 'instrument'])
	#status, artists, msg = dao.getArtistsRelations(rel_table='recording', relation=['vocal', 'instrument'], collection='Ottoman')
	#for artist in artists:
		#print artist
	#print len(artists)
	
	status, tags, msg = dao.getTags("0071586b-a9f4-4f89-a766-87f77ee12f81")
	print tags
	print "AKIIIIIIIIIIIIII"
	status, recordings, msg = dao.getRecordings(uuid="7344b268-741a-444f-81ed-f7c89fefe020")
	print recordings
