import email_data
import model
import time, os
import tensorflow as tf
tf.keras.backend.set_floatx('float16')

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

emails = email_data.parse_outlook_emails_from_file("emails.json")
print(emails[8].title)

gemma = model.Gemma2Model()

s = time.time()
events = gemma.parse_events_from_emails([emails[8]])
elapsed = (time.time() - s) / 60
print(events)
print(f"TOOK {elapsed} s")

s = time.time()
events = gemma.parse_events_from_emails([emails[7]])
elapsed = (time.time() - s) / 60
print(events)
print(f"TOOK {elapsed} s")
