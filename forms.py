from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired

class PredictForm(FlaskForm):
    STATE = StringField('State', validators=[DataRequired()])
    Temp = FloatField('Temp', validators=[DataRequired()])
    DO= FloatField('D.O.', validators=[DataRequired()])
    PH = FloatField('PH', validators=[DataRequired()])
    CONDUCTIVITY = FloatField('CONDUCTIVITY', validators=[DataRequired()])
    BOD= FloatField('B.O.D.', validators=[DataRequired()])
    NITRATE_NITRITE = FloatField('NITRATE_NITRITE', validators=[DataRequired()])
    FECAL_COLIFORM = FloatField('FECAL_COLIFORM', validators=[DataRequired()])
    TOTAL_COLIFORM = FloatField('TOTAL_COLIFORM', validators=[DataRequired()])
    submit = SubmitField('Predict')
    result = ""  # To store the prediction result
