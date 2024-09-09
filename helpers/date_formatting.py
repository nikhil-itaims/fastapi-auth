def format_date(date):
    desired_format = "%A, %b %d %Y %H:%M %p"
    return date.strftime(desired_format)

def get_only_date_year(date):
    desired_format = "%b %d, %Y"
    return date.strftime(desired_format)
