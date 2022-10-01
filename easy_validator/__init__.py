
class Validator:
	def __init__(self,framework=None,**validators):
		self.__validators=validators
		self.__framework=framework
		self._required=[]
		
		for elem in validators:
			

			def validator(required):
				if required:
					self._required.append(required)

				return validators[elem](
					required=required,
					**config)
			return validator




			setattr(self,elem,
				lambda required=False,**config:validator(required,**config))


	def __call__(self,validator):
		import inspect
		from functools import wraps
		def decorator(fn):
			
			if self.__framework=="flask":
				from flask import jsonify
				@wraps(fn)
				def wrapper(*params,**kwargs):
	
					try:
						validator()
					except ValidationError as e:

						return jsonify({"ValidationError":str(e)}),500

					return {"ValidationError":str(e)}
				return fn(*params,**kwargs)

		
			elif self.__framework=="quart":
				from quart import jsonify
				@wraps(fn)
				async def wrapper(*params,**kwargs):

					try:
						await validator()
						
					except ValidationError as e:
						
						return jsonify({"ValidationError":str(e)}),500
					return await fn(*params,**kwargs)
				
		

			return wrapper
		return decorator

	def validate(self,data,schema):
		for elem in schema:
			path=elem.split(".")

			item=data[path[0]]
			for p in path[1:]:
				item=item[p]
		
			if not schema[elem](item):
				for valid in dir(self):
					if not valid.startswith("_") and valid not in ["validate"]:
						if valid==schema[elem].__name__:
							raise ValidationError(f"Dato '{elem}' no es valido para {valid}")
		self._required=[]
		return True

class UtilValidator(Validator):
	
	def is_isoformat(self,required=False):
		self._required.append(required)

		def is_isoformat(date_string):
			"""Valida si una cadena de texto es isoformat 

			>>> is_isoformat('2022-09-30T00:25:40.338953')
			True
			"""
			from datetime import datetime
			try:
			    datetime.fromisoformat(date_string)
			    return True
			except ValueError:
				return False

		return is_isoformat

class ValidationError(Exception):
	pass
util_validator=UtilValidator()
if __name__=="__main__":
	import doctest
	doctest.testmod(verbose=True)