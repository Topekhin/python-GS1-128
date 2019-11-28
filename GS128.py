import json
import re


class GS128(object):

    def __init__(self):
        self.errorMessage = ''
        with open('GS128.json', 'r', encoding='utf-8') as fh:
            self.identifiers = json.load(fh) 


    def _getData(self, data, pointer, size):
        if pointer + size > len(data):
            return None

        result = data[pointer:pointer+size]
        return result
    

    def _decode_field(self, field):
        if len(field) == 0:
            return None, None, None, False

        pointer = 0
        identificator = self._getData(field, pointer, 2)
        if identificator == None:
            return None, None, None, False
        
        id_string = identificator.decode('utf-8')

        try:
            dict = self.identifiers[id_string]
            pointer = pointer + 2
        except:
            print("GS128: Identifier " + id_string + " is unknown")
            return None, None, None, False

        try:
            length = dict["Length"]
        except:
            print("GS128: Identifier " + id_string + " does not have the <Length> parameter")
            return None, None, None, False


        if length != 0:
            value = self._getData(field, pointer, length)
            print("("+id_string+") "+ dict["Description"] + ": " + value.decode('utf-8'))
            return field[pointer + length:], id_string, value.decode('utf-8'), True
        else:
            value = field[pointer:]
            print("("+id_string+") "+ dict["Description"] + ": " + value.decode('utf-8'))
            return None, id_string, value.decode('utf-8'), True

    def decode(self, code):
        if isinstance(code, bytes) == False:
             code = code.encode('utf-8')

        if code[0] == 29:
            code = code[1:]
        else:
            print('WARNING: Not correct GS1-128 code: FNC1 character not found.')

        fields = re.split(b'\x1d', code)
        result = dict()

        for field in fields:
            while(1):
                field, id_string, value, valid = self._decode_field(field)
                if valid == False:
                    return dict(), False # Critical error, stop
                if id_string != None and value != None:
                    result.update( { id_string : value } )
                if field == None:
                    break
        return result, True


