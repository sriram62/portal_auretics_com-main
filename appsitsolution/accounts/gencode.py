import string
# Specified Digits to be taken for creating userid
digs = "0123456789AXCDEFGHYJKLMNZPQRTUV"

# Modified version taken from https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base
def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)

def AGmod_base10(number, number_to_be_added):
    added_number = int(number) + int(number_to_be_added)
    if added_number >= 10:
        added_number = added_number - 10

    return(added_number)

numbers = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", 1, 2, 3, 4, 5, 6, 7, 8, 9, 0}
letters = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
           "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
           "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}

def generate_refcode_base_AGmod(userid=0,upline=0,PAN="1234567890",lastname="7"):
    # Convert inputs into integers
    # Checking if Upline argument is found. Note: 0 at the end of the upline's userid is possible (and frequent).
    # Upline digit W means some error.
    try:
        upline = int(str(upline)[-1])
        if upline == " ":
            upline = "W"
    except:
        upline = "W"
    # Check userid : userid should be more than 0.
    try:
        userid = int(userid)
        if userid <= 0:
            return ValueError
    except:
        return ValueError

    # Convert userid into base10 format of 9 digits (eg: 123 will become 000000123)
    if len(str(userid)) < 9:
        i = 9 - len(str(userid))
        zeroes_to_be_added = ""
        while i > 0:
            zeroes_to_be_added = zeroes_to_be_added + "0"
            i = i - 1
        userid_base10 = zeroes_to_be_added + str(userid)
    else:
        userid_base10 = str(userid)

    # Add values to base10 format as per AGmod requirements  i.e.   (5) 1	9	2	8	3	7	4	6	5
    # These figures will be added individually (digit by digit) to the base10 format and if a numeric letter exceeds 9 then it will be substracted by 10.
    AGmod_additions = "19283746500000000000"
    moded_userid_base10 = ""
    for digit in range(0,len(userid_base10)):
        moded_userid_base10 = moded_userid_base10 + str(AGmod_base10(list(userid_base10)[digit],list(AGmod_additions)[digit]))
    moded_userid_base_AGMod = int2base(int(moded_userid_base10),31)
    # Add paddings : Few userid's might be less than 6 characters, so we will add W at the end of the moded userid to make len = 6
    if len(str(moded_userid_base_AGMod)) < 6:
        i = 6 - len(str(moded_userid_base_AGMod))
        w_to_be_added = ""
        while i > 0:
            w_to_be_added = w_to_be_added + "W"
            i = i - 1
        moded_userid_base_AGMod_padded = moded_userid_base_AGMod + str(w_to_be_added)
    else:
        moded_userid_base_AGMod_padded = str(moded_userid_base_AGMod)
    # Adding Upline's last digit + 1 to the userid so that upline can see who is how much down/up the user is to them
    try:
        upline_last_digit = int(upline)

        if upline_last_digit == 9:
            digit_to_be_added = 0
        else:
            digit_to_be_added = upline_last_digit + 1
    except:
        digit_to_be_added = "W"
    try:
        user_PAN = str(PAN)[4].upper()
        if user_PAN == " ":
            user_PAN = "4"
        if user_PAN in numbers:
            user_PAN = 1
        elif user_PAN in letters:
            pass
        else:
            user_PAN = 2
    except:
        try:
            # Error in PAN number. Does not exist. Usually this means that the PAN number entered is incorrect (less than 5 digits).
            # In this case we will add first letter of his last Name
            # Can be some different error as well.
            user_PAN = str(lastname)[0].upper()
            if user_PAN == " ":
                user_PAN = "4"
            if user_PAN in numbers:
                user_PAN = 1
            elif user_PAN in letters:
                pass
            else:
                user_PAN = 2
        except:
            # user_PAN = "3"        # removed after sep-2021
            user_PAN = "5"
    final_userid = str(user_PAN) + str(moded_userid_base_AGMod_padded) + str(digit_to_be_added)
    return final_userid

# # For Testing
# while True:
#     print("Enter UserID:")
#     input_number = input()
#     print("Enter Upline Code:")
#     input_upline = input()
#     print("Enter User PAN:")
#     input_PAN = input()
#     print(generate_refcode_base_AGmod(input_number,input_upline, input_PAN))
#
# # Automatic Testing:
# for i in range(10000000):
#     # print("Enter UserID:")
#     input_number = i
#     # print("Enter Upline Code:")
#     input_upline = 1
#     # print("Enter User PAN:")
#     input_PAN = i
#     print(generate_refcode_base_AGmod(input_number,input_upline, input_PAN))

def genReferralCode(UserID,UplineCode,PAN,lastname):
    referralCode = generate_refcode_base_AGmod(UserID,UplineCode,PAN,lastname)
    return referralCode
