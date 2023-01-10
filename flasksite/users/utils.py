import os
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

def save_picture(form_picture):
    picture_fn = secure_filename(form_picture.filename)
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