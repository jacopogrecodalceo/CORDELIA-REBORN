# cordelia/errors.py

class CordeliaError(Exception):
	"""Base class for all Cordelia errors"""
	def __init__(self, message: str, code: str = None, suggestion: str = None, context: dict = None):
		self.message = message
		self.code = code
		self.suggestion = suggestion
		self.context = context or {}
		super().__init__(message)

class CordeliaTransformerError(CordeliaError):
	"""Raised when transformation fails"""
	pass

class CordeliaValidationError(CordeliaError):
	"""Raised when validation fails"""
	pass

class CordeliaDeductionError(CordeliaError):
	"""Raised when deduction/inference fails"""
	pass

class CordeliaParseError(CordeliaError):
	"""Raised when parsing fails"""
	pass

class CordeliaTypeError(CordeliaError):
	"""Raised when type checking fails"""
	pass

class CordeliaSyntaxError(CordeliaError):
	"""Raised when syntax is invalid"""
	pass

class CordeliaRuntimeError(CordeliaError):
	"""Raised when runtime execution fails"""
	pass

class CordeliaNotFoundError(CordeliaError):
	"""Raised when something is not found"""
	pass

class CordeliaInitError(CordeliaError):
   pass

class CorpusError(CordeliaError):
   pass
