from fastapi import File, HTTPException, UploadFile, status
import tensorflow as tf 
from keras.applications import VGG16
import numpy as np
import uuid
import cv2
new_input_shape = (500, 500, 3)
model = VGG16(weights='imagenet', include_top=False, input_shape=new_input_shape,pooling='avg')

def preprocess_image(image_path, target_size=(500, 500)):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Convert to RGB
    img = cv2.resize(img, target_size)
    img = img.astype(np.float32) / 255.0 # Normalize
    return img

def extract_features(img, model):
    # Reshape the image to match VGG input shape)
    img = np.expand_dims(img, axis=0)
    # Extract features
    features = model.predict(img)
    return features.flatten()  # Flatten the feature

async def embeding_photo(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()
    #save the file
    with open(f"../frontend_v1/public/images/{file.filename}", "wb") as f:
        f.write(contents)
    try:
        ret = preprocess_image(image_path=f"../frontend_v1/public/images/{file.filename}")
        return (extract_features(ret, model), f"images/{file.filename}")
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the embeding process")
    
