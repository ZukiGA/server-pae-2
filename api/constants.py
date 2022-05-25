HOUR_CHOICES = [x for x in range(7, 18)]  #[7, 17]
PERIOD_CHOICES = [0, 1, 2]
DAY_WEEK_CHOICES = [0, 1, 2, 3, 4]

NAME_RE = "^[a-zA-Zñá-úÁ-Úü]([.](?![.])|[ ](?![ .])|[a-zA-Zñá-úÁ-Úü])*$"
EMAIL_RE = "^a[0-9]{8}@tec.mx"
