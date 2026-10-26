from pydantic import BaseModel


class Contact_scheme(BaseModel):
    first_name: str
    last_name: str
    your_email: str
    message: str

class ContactID_scheme(Contact_scheme):
    id: str