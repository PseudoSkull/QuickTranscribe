# WS_collection
import requests
from openai_api_key import api_key
import base64

endpoint = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

# # OpenAI API Key
# api_key = "YOUR_OPENAI_API_KEY"

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "projectfiles/test_image.png"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

# Indent lines of the poem (indented from the lowest verse) by using the colon \":\", and remember this is going on MediaWiki, so fine tune it for wiki styling.

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
        #   "text": "Read exactly what is on this page to me, without correcting ANYTHING. DO NOT READ ANY HEADERS OR FOOTERS. Omit hyphens ending a line unless meaningful. Do not provide any explanations."
          "text": "Read exactly what is on this page to me except headers and footers, without correcting ANYTHING.Do not provide any explanations."
        #   "text": "Identify which phrases/words in the text are in italics, and then send them to me in JSON format. Associate an array of instances of the phrase in the text. Items should look like this: \"this;\": [2, 3, 5]. That represents the second 'this;', the third 'this;', and the fifth 'this;'. IF THERE ARE NONE, SENT ME AN EMPTY JSON BIT. Do not provide any explanations."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 3000
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())




# data = {
#     'model': 'gpt-3.5-turbo',  # Use the latest GPT-3 model
#     'messages': [
#         {'role': 'system', 'content': 'You are an expert transcriptionist. Your job is to take bits of OCR from books from the early 20th century, and correct the text on them as much as possible to fit what the actual text probably said. Honor the original texts as much as possible. The following is only a single page. DO NOT GENERATE MORE TEXT than what\'s already here. Just correct what\'s there. Specific rules: If there\'s no punctuation at the end, leave it as is. It probably means the sentence continues on the next page. DO NOT END IT WITH ... IF THAT DOESN\'T APPEAR THERE!'},
#         {'role': 'user', 'content': """THERE be no use talking o* holidays this year! "said Mehitable rather bitterly, the swift—a wooden apparatus for winding yarn, fastened to the edge of the table with a thumbscrew—turning rapidly as she spoke. For this was the time of the Revolution and the American soldiers must be clad.

# "I suppose not," agreed Charity, looking up from her seam with a sigh as she reached over to change the cloth in the beak of her sewing bird.
# "The parrot. Father!" prompted both girls eagerly.

# "Oh yes. I verily believe you know this tale better than I!" he laughed. "Well, I had pressed forvard most anxiously after my father when 'Polly wants a cracker!* said the bird, and 'Polly wants a cracker!* imitated a pert voice behind me. I turned around indignantly to see a little girl with very red hair staring at me saucily from behind her mother's skirts."

# "Oh, Samuel, not very red hair!" protested Mistress Condit with a furtive pat at the auburn curls that peeped beneath her cap.
# "Of course it is, silly!" burst out Mehitable. "And the little red-haired girl was Mother, wasn't she. Father.?"

# "T"ow, that," said the Squire judicially, "is the question. Howbeit, to finish my tale before the apples burn." He glanced significantly at the row of scorching Jonathans which Mehitable promptly turned. "One day little Mary appeared with drooping face. *My head doth ache!' quoth she, and she coughed, though it was a clear, warm day.

# "Her mother bundled her down the ship's cabin, but not before I had stolen a kiss, for by that time I loved little Mary as dearly as ten years can love eight years. Then it was announced that little Mary had the measles!\""""}
#     ],
#     'max_tokens': 3000,  # Request a longer response
#     'temperature': 0,  # Control the randomness of the response
#     'top_p': 0,  # Control the diversity of the response
# }

# response = requests.post(endpoint, json=data, headers=headers)

# if response.status_code == 200:
#     print(response.json())
# else:
#     print('Failed to fetch data:', response.status_code, response.text)
