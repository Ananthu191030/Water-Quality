from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired

class PredictForm(FlaskForm):
    STATE = StringField('State', validators=[DataRequired()])
    Temp = FloatField('Temperature', validators=[DataRequired()])
    DO = FloatField('D.O (mg/l)', validators=[DataRequired()])
    PH = FloatField('pH', validators=[DataRequired()])
    CONDUCTIVITY = FloatField('Conductivity (µhos/cm)', validators=[DataRequired()])
    BOD = FloatField('B.O.D (mg/l)', validators=[DataRequired()])
    NITRATE_NITRITE = FloatField('Nitrate+Nitrite (mg/l)', validators=[DataRequired()])
    FECAL_COLIFORM = FloatField('Fecal Coliform (MPN/100ml)', validators=[DataRequired()])
    TOTAL_COLIFORM = FloatField('Total Coliform (MPN/100ml)Mean', validators=[DataRequired()])
    submit = SubmitField('Predict')
    result = None  # To store the prediction result
