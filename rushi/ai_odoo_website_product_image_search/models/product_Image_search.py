# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from odoo.http import request
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.efficientnet import EfficientNetB0, preprocess_input


class ImageSearchEngine:

    def __init__(self):
        self.embedding_model = EfficientNetB0(include_top=False, weights='imagenet', pooling='avg')

    def compute_image_embedding_from_path(self, image_data: bytes):
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((224, 224))
        img_array = keras_image.img_to_array(img)
        img_array = preprocess_input(img_array)
        x = np.expand_dims(img_array, axis=0)
        embedding = self.embedding_model.predict(x, verbose=0)[0]
        embedding /= np.linalg.norm(embedding)
        return embedding  # NumPy array

    def connect_to_db(self):
        db_name = request.env.cr.dbname
        db = odoo.sql_db.db_connect(db_name)
        return db

    def create_embedding_table(self, table_name):
        query = f"""
           CREATE TABLE IF NOT EXISTS "{table_name}" (
               id SERIAL PRIMARY KEY,
               product_id INT,
               title TEXT,
               embedding float8[],
               record_type TEXT
           );
       """
        request.env.cr.execute(query)

    def predict_with_python_similarity(self, image_data: bytes, table_name: str, top_n: int, max_distance_threshold=0.3, search_type='product'):
        try:
            input_vector = self.compute_image_embedding_from_path(image_data)
            query = f"""
                SELECT product_id, title, embedding, record_type
                FROM "{table_name}"
                WHERE record_type = %s
            """
            request.env.cr.execute(query, (search_type,))
            records = request.env.cr.fetchall()

            results = []
            for product_id, title, embedding_list, record_type in records:
                if embedding_list:
                    embedding_array = np.array(embedding_list)
                    similarity = np.dot(input_vector, embedding_array)
                    results.append({
                        "product_id": product_id,
                        "title": title,
                        "similarity": float(similarity),
                        "record_type": record_type
                    })

            results.sort(key=lambda x: x["similarity"], reverse=True)
            filtered = [r for r in results if r["similarity"] >= 1 - max_distance_threshold][:top_n]

            return {
                "status": "success",
                "closest_products": filtered,
                "statistics": {
                    "mean_similarity": float(np.mean([r["similarity"] for r in filtered])) if filtered else 0,
                    "min_similarity": float(np.min([r["similarity"] for r in filtered])) if filtered else 0,
                    "max_similarity": float(np.max([r["similarity"] for r in filtered])) if filtered else 0,
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
