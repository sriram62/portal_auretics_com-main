# Checking email id pattern
email = "arjun@auretics.com"
email_split = list(email)
print(email_split)
email_status = False
if "@" in email:
    if "." in email:
        if " " not in email:
            email_status = True
print(email_status)