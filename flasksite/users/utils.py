import os
from PIL import Image
from flask import current_app
import secrets

def save_picture(form_picture):
    _, ext = os.path.splitext(form_picture.filename)
    picture_fn = secrets.token_hex(8) + ext
    picture_path = os.path.join(current_app.root_path, 'static/prof_pict', picture_fn)

    i = Image.open(form_picture)
    output_size = (125, 125)
    i.thumbnail(output_size)
    width, height = i.size
    offset  = int(abs(height-width)/2)
    if width>height:
        i = i.crop((offset,0,width-offset,height))
    elif height>width:
        i = i.crop((0,offset,width,height-offset))
    i.save(picture_path)

    return picture_fn

def delete_picture(filename):
    picture_path = os.path.join(current_app.root_path, "static/prof_pict", filename)
    os.remove(picture_path)