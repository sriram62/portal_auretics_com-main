import io
import os.path

from PIL import Image, ImageFont, ImageDraw
from django.conf import settings

from mlm_calculation.models import title_qualification_calculation_model


class GreetingBaseTemplate:
    # Font Paths
    base = settings.STATICFILES_DIRS[0]
    greeting_font_path = os.path.join(base,
                                      "fonts/capenhood free personal.ttf")  # "D:\Work\WiftCap\Code\portal_auretics_com_files\capenhood free personal.ttf"
    user_data_font_path = os.path.join(base,
                                       "fonts/CAXTON Bold BT.ttf")  # D:\Work\WiftCap\Code\portal_auretics_com_files\caxton-bk-bt-cufonfonts\CAXTON LT Light.TTF"
    user_name_font_path = os.path.join(base,
                                       "fonts/capenhood free personal.ttf")  # D:\Work\WiftCap\Code\portal_auretics_com_files\caxton-bk-bt-cufonfonts\CAXTON Bold BT.ttf"

    # Font Sizes
    user_name_font_size = 75
    user_data_font_size = 55
    user_data_line_space = 78

    # Font Colors
    # greeting_font_color = (50, 50, 150)
    user_data_font_color = (50, 50, 50)

    # Element Sizes
    template_size = (1280, 1280)
    user_photo_size = (450, 450)

    # Element Positions
    user_data_position = (1200, 850)
    user_photo_position = (80, 780)

    # User data alignment (either left or right)
    user_data_alignment = 'right'

    # save_path = r'D:\Work\WiftCap\Code\portal_auretics_com_files\Sample images\template_test.jpg'

    def __init__(self, user, background_image_path=None):
        self.user = user
        # TODO: Make sure changes to model are not saved
        self.user.title_label = "Title: "
        self.user.arn_label = "ARN: "
        self.user.contact_label = "Mobile: "
        self.user_photo_path = user.profile.avatar
        self.background_image_path = background_image_path
        self._create_template()

    def _get_title_position(self, offset: tuple):
        greeting_x = self.template_image.size[0] // 2 + offset[0]
        greeting_y = self.template_image.size[1] // 2 + offset[1]
        return greeting_x, greeting_y

    @staticmethod
    def _concatenate_text(text1, font1, text2, font2, image):
        pass

    def _create_template(self):
        if self.background_image_path:
            self.template_image = Image.open(self.background_image_path)
        else:
            bg_colour = (255, 255, 255, 255)
            self.template_image = Image.new("RGBA", self.template_size, bg_colour)

        self.image_draw_object = ImageDraw.Draw(self.template_image)
        self.image_draw_object.fontmode = "L"

        self._draw_user_data()
        self._draw_profile_photo()
        # self._draw_title()

    # def _draw_title(self):
    #     title_offset = (self.greeting_offset_x, self.greeting_offset_y)
    #     title_font = ImageFont.truetype(self.greeting_font_path, self.title_font_size)
    #     title_x, title_y = self._get_title_position(title_offset)
    #
    #     self.image_draw_object.text((title_x, title_y), self.greeting_text, font=title_font,
    #                                 fill=self.greeting_font_color,
    #                                 anchor='md')

    def _get_full_name_wa(self):
        name = self.user.profile.first_name + " " + self.user.profile.last_name
        if len(name) >= 15:
            name = self.user.profile.first_name
            if len(name) >= 15:
                name = name[:15]
        return name

    def _draw_user_data(self):
        user_name_font = ImageFont.truetype(self.user_name_font_path, self.user_name_font_size)
        user_data_font = ImageFont.truetype(self.user_data_font_path, self.user_data_font_size)

        try:
            title_qs = title_qualification_calculation_model.objects.filter(
                user=self.user,
                calculation_stage='Public').latest('pk').highest_qualification_ever
        except:
            title_qs = 'Associate Advisor'

        self._draw_data(self._get_full_name_wa(), 1, user_name_font)
        self._draw_data(self.user.title_label + " " + title_qs, 2, user_data_font)
        # self._draw_data(self.user.arn_label + " " + self.user.referral_id, 3, user_data_font)
        self._draw_data(self.user.arn_label + " " + self.user.referralcode.referral_code, 3, user_data_font)
        self._draw_data(self.user.contact_label + " " + self.user.profile.phone_number, 4, user_data_font)

    # self.image_draw_object.multiline_text((150, 150), "This is\na multiline\ntext", (0, 0, 0), font=user_data_font)
    def _draw_data(self, text, position, font):
        if self.user_data_alignment == 'left':
            # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
            anchor = 'lt'
        elif self.user_data_alignment == 'center':
            anchor = 'mt'
        else:
            anchor = 'rt'
        self.image_draw_object.text(
            (self.user_data_position[0], self.user_data_position[1] + (self.user_data_line_space * position)), text,
            font=font, fill=self.user_data_font_color, anchor=anchor)

    def _draw_profile_photo(self):
        self.profile_photo = Image.open(self.user_photo_path)
        self.profile_photo = self.profile_photo.resize(self.user_photo_size, )

        crop_circle_mask = Image.new('RGBA', self.profile_photo.size, (255, 255, 255, 0))
        mask_draw = ImageDraw.Draw(crop_circle_mask)
        # photo_position = [100, 750]
        mask_draw.ellipse(((0, 0), self.profile_photo.size), fill=(255, 255, 255, 255), outline=5)
        # crop_circle_mask.show()

        self.template_image.paste(self.profile_photo, self.user_photo_position, crop_circle_mask)

    def get_preview_image_bytes(self):
        img_bytes_array = io.BytesIO()
        self.template_image.save(img_bytes_array, format='PNG')
        import base64
        return base64.b64encode(img_bytes_array.getvalue()).decode()

    def show(self):
        self.template_image.show()

    def save_preview_image(self, save_path):
        self.template_image.save(save_path)


class Template2(GreetingBaseTemplate):
    user_name_font_size = 70
    user_data_font_size = 45
    # Element Sizes
    user_photo_size = (350, 350)

    # Element Positions
    user_data_position = (40, 670)
    user_photo_position = (700, 700)

    user_data_alignment = 'left'


if __name__ == '__main__':
    class User: pass


    user = User()
    user.name = "Palvinder Singh"
    user.title_label = "Title: "
    user.title = "Associate Director"
    user.arn_label = "ARN: "
    user.referral_id = "35NSNJM6"
    user.contact_label = "Mobile: "
    user.phone_number = "8950075611"
    user.profile_photo_path = r"D:\Work\WiftCap\Code\portal_auretics_com_files\Sample images\WhatsApp Image 2022-04-25 at 8.00.56 PM.jpeg"

    # background_image_path = r"D:\Work\WiftCap\Code\portal_auretics_com_files\Sample images\Postcard_1280x1280.jpg"
    background_image_path = r"D:\Work\WiftCap\Code\portal_auretics_com_files\Sample images\crystal background.jpg"

    template = GreetingBaseTemplate(user, background_image_path)
    template.save_preview_image(r"D:\Work\WiftCap\Code\portal_auretics_com_files\Sample images\template_test.png")

    left_align_template = Template2(user, background_image_path)
    left_align_template.save_preview_image(
        r"D:\Work\WiftCap\Code\portal_auretics_com_files\Sample images\template_test_left_align.png")
