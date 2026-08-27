class Person:
    def __init__(self , name :str , age:int , address:str , phone:str):
        self.name = name
        self.age = age
        self.address = address
        self.phone = phone
    def to_dic(self):
        return{
            "name":self.name , 
             "age":self.age , 
             "address":self.address ,
             "phone":self.phone

        }    
        
	