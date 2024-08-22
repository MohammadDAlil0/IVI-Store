from fastapi import File, HTTPException, UploadFile, status
import tensorflow as tf 
import numpy as np
import uuid
import cv2
new_input_shape = (300, 300, 3)
import keras
model = keras.models.load_model('./m_class_epoch_03_val_acc_0.9788.keras')

def preprocess_image(image_path, target_size=(300, 300)):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Convert to RGB
    img = cv2.resize(img, target_size)
    img = img.astype(np.float32) / 255.0 # Normalize
    return img

async def class_photo(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()
    
    # Save the file
    image_path = f"../frontend_v1/public/images/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(contents)

    try:
        # Preprocess the image
        img = preprocess_image(image_path=image_path)
        
        # Add batch dimension
        img = np.expand_dims(img, axis=0)  # Shape (1, 300, 300, 3)
        
        # Make prediction
        predictions = model.predict(img)
        
        # Process predictions (this will depend on your model's output)
        predicted_class = np.argmax(predictions, axis=1)  # Assuming classification task
        return {"predicted_class": int(predicted_class[0])}

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong during the embedding process.")
