from datetime import datetime,timedelta
import requests

class Domain():
	def __init__(self,nam_domain,int_time_limit_between_requests):
		self.time_last_access = datetime(1970,1,1)
		self.nam_domain = nam_domain
		self.int_time_limit_seconds  = int_time_limit_between_requests
	@property
	def time_since_last_access(self):
		time = datetime.now()
		return time - self.time_last_access

	def accessed_now(self):
		self.time_last_access = datetime.now()

	def is_accessible(self):
		time = self.time_since_last_access.seconds

		if self.int_time_limit_seconds <= time:
			req = requests.get("http://" + self.nam_domain.strip("http://"))
			if req.status_code == 200:
				return True
			else:
				return False
		else:
			return False

	def __eq__(self, domain):
		if type(domain) is str:
			return domain == self.nam_domain
		else:
			return domain.nam_domain == self.nam_domain

	def __str__(self):
		return self.nam_domain

	def __repr__(self):
		return str(self)

	def __hash__(self):
		return hash(self.nam_domain)
