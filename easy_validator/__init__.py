
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
                        validator(*params,**kwargs)
                    except ValidationError as e:

                        return jsonify({"ValidationError":str(e)}),500
                    except ValidationRequired as e:
                        return jsonify({"ValidationRequired":str(e)}),500


                    return fn(*params,**kwargs)

        
            elif self.__framework=="quart":
                from quart import jsonify
                @wraps(fn)
                async def wrapper(*params,**kwargs):
                    
                    try:
                        await validator(*params,**kwargs)
                        
                    except ValidationError as e:
                        print({"ValidationError":str(e)})
                        return jsonify({"ValidationError":str(e)}),500
                    except ValidationRequired as e:
                        return jsonify({"ValidationRequired":str(e)}),500

                    return await fn(*params,**kwargs)
                
        

            return wrapper
        return decorator

    def validate(self,data,schema):

        for index,elem in enumerate(schema):
            path=elem.split(".")
            required=False
            
            if "required" in dir(schema[elem]):
                required=True
            
            if path[0] not in data and required:
                raise ValidationRequired(f"Validación requerida para '{path[0]}'")
            if path[0] not in data:
                continue
            item=data[path[0]]
            _path=path[0]
       
            for p in path[1:]:
                _path+="."+p
                if type(item)==dict:
                    if p not in item.keys():
                
                        raise ValidationError(f"key '{_path}' not in {item.keys()}")
                    item=item[p]
                elif p.isdigit():
                    item=item[int(p)]
               

            if callable(schema[elem]) and not schema[elem](item):
                
                for valid in dir(self):
                 
                    if not valid.startswith("_") and valid not in ["validate"]:
                        if valid==schema[elem].__name__:
                            raise ValidationError(f"Dato '{elem}' no es valido para {valid}")
            elif type(schema[elem]) in [list,tuple]:
                l=[]
                for v in schema[elem]:
                    l.append(v(item))
              
                if not any(l):
                    raise ValidationError(f"Dato '{elem}' no es valido")


        self._required=[]
        return True

class UtilValidator(Validator):

    def is_structure(self,structure:dict,null=False,required=False):
     

        def is_structure(data:dict):
            if structure==None and null:
                return True

            def recursive(data,structure):
                l=[]
                for elem in data:
                    if callable(structure[elem]):
                        l.append(structure[elem](data[elem]))
                    elif type(data[elem])==dict:
                        l.append(recursive(data[elem],structure[elem]))
                return all(l)

            l=[]
            for elem in data:

                if callable(structure[elem]):
                    l.append(structure[elem](data[elem]))
                elif type(data[elem])==dict:
                    l.append(recursive(data[elem],structure[elem]))
            return all(l)
        is_structure.required=required
        return is_structure
    
    def is_image_file(self,required=False):
        def is_image_file(string):
            for elem in [".jpg",".png",".bmp",".svg",".jpeg"]:

                if string.lower().endswith(elem):
                    return True
            return False
        is_image_file.required=required
        return is_image_file

    def is_extension(self,extend:list,required=False):
        def is_extension(string):
            for elem in extend:
                if string.lower().endswith(elem):
                    return True
            return False
        is_image_file.required=required
        return is_image_file

    def exists_register(self,session,model,required=False,**fields):
        def exists_register(string):
            for elem in extend:
                query={}
                for field in fields:
                    query[getattr(model,field)]=fields[field]
                instance=session.query(model).filter(query).first()
                if instance:
                    return True
            return False
        exists_register.required=required
        return exists_register

    def is_isostringformat(self,null=False,required=False):
        

        def is_isostringformat(date_string):
            """Valida si una cadena de texto es isoformat 

            >>> is_isoformat('2022-09-30T00:25:40.338953')
            True
            """

            from datetime import datetime
            if date_string==None and null:
                return True
            try:
                datetime.strptime(date_string,"%Y-%m-%dT%H:%M:%S.%fZ")
                return True
            except ValueError:
                return False
        is_isostringformat.required=required
        return is_isostringformat

    def is_isoformat(self,null=False,required=False):
        

        def is_isoformat(date_string):
            """Valida si una cadena de texto es isoformat 

            >>> is_isoformat('2022-09-30T00:25:40.338953')
            True
            """
            if date_string==None and null:
                return True
            from datetime import datetime
            try:
                datetime.fromisoformat(date_string)
                return True
            except ValueError:
                return False
        is_isoformat.required=required
        return is_isoformat

    def is_menor(self,paths,transformer,null=False,required=False):
        

        def is_menor(data):
            """Valida si una cadena de texto es isoformat 

            >>> is_isoformat('2022-09-30T00:25:40.338953')
            True
            """
            if data==None and null:
                return True
            for start,end in paths:
                item=data[path[0]]
                _path=path[0]
                for p in path[1:]:
                    _path+="."+p
                    if type(item)==dict:
                        if p not in item.keys():
                            
                            raise ValidationError(f"key '{_path}' not in {item.keys()}")
                        item=item[p]
                    elif p.isdigit():
                        item=item[int(p)]

                if not (transformer(start)<transformer(end)):
                    return False

            return True

    
        is_menor.required=required
        return is_menor

def replace(data,path,fn):
    path=path.split(".")
    item=data[path[0]]
    for k,p in enumerate(path[1:]):

        if p in item:
            
            if k+1==len(path[1:]):
                item[p]=fn(item[p])

            else:
                item=item[p]
        else:
            break

def replace_default(data:dict,default:dict):
    def recusive(data,default):
        for elem in default:
            if elem not in data:
                data[elem]=default[elem]
            elif type(data[elem])==dict:
                recusive(data[elem],default[elem])
    if type(data)==dict:
        recusive(data,default)

class ValidationError(Exception):
    pass
class ValidationRequired(Exception):
    pass
def check(fn=lambda x:True,required=False):
    fn.required=required
    return fn
def group(*validators):
    required=False
    for validator in validators:
        if validator.required:
            required=True
            break
    def wrapper(x):
        for validator in validators:
            validator(x)
    wrapper.required=required
    return wrapper

def from_isostring(str_date):
    return date_time.strptime(str_date,"%Y-%m-%dT%H:%M:%S.%fZ")

def to_isostring(date_time):
    return date_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
util_validator=UtilValidator("quart")
if __name__=="__main__":
    import doctest
    doctest.testmod(verbose=True)