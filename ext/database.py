from flask_sqlalchemy import SQLAlchemy as SQLAlchemyBase
import sys
sys.path.append("..")

from models.base import set_query_property

class SQLAlchemy(SQLAlchemyBase):
    """ Extensão do FLASK que integra o alchemy com o Flask-SQLAlchemy. """
    def __init__(self,
                 app=None,
                 use_native_unicode=True,
                 session_options=None,
                 Model=None):
        self.Model = Model

        super(SQLAlchemy, self).__init__(app,use_native_unicode,session_options)

    def make_declarative_base(self,model_class=None, metadata=None):
        """Creates or extends the declarative base."""
        if self.Model is None:
            self.Model = super(SQLAlchemyBase, self).make_declarative_base()
        else:
            set_query_property(self.Model, self.session)
        return self.Model