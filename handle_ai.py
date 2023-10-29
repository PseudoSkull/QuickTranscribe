# WS_collection
import requests
from openai_api_key import api_key

endpoint = 'https://api.openai.com/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}







data = {
    'model': 'gpt-3.5-turbo',  # Use the latest GPT-3 model
    'messages': [
        {'role': 'system', 'content': 'You are an expert transcriptionist. Your job is to take bits of OCR from books from the early 20th century, and correct the text on them as much as possible to fit what the actual text probably said. Honor the original texts as much as possible. The following is only a single page. DO NOT GENERATE MORE TEXT than what\'s already here. Just correct what\'s there. Specific rules: If there\'s no punctuation at the end, leave it as is. It probably means the sentence continues on the next page. DO NOT END IT WITH ... IF THAT DOESN\'T APPEAR THERE!'},
        {'role': 'user', 'content': """THERE be no use talking o* holidays this year! "said Mehitable rather bitterly, the swift—a wooden apparatus for winding yarn, fastened to the edge of the table with a thumbscrew—turning rapidly as she spoke. For this was the time of the Revolution and the American soldiers must be clad.

"I suppose not," agreed Charity, looking up from her seam with a sigh as she reached over to change the cloth in the beak of her sewing bird.
"The parrot. Father!" prompted both girls eagerly.

"Oh yes. I verily believe you know this tale better than I!" he laughed. "Well, I had pressed forvard most anxiously after my father when 'Polly wants a cracker!* said the bird, and 'Polly wants a cracker!* imitated a pert voice behind me. I turned around indignantly to see a little girl with very red hair staring at me saucily from behind her mother's skirts."

"Oh, Samuel, not very red hair!" protested Mistress Condit with a furtive pat at the auburn curls that peeped beneath her cap.
"Of course it is, silly!" burst out Mehitable. "And the little red-haired girl was Mother, wasn't she. Father.?"

"T"ow, that," said the Squire judicially, "is the question. Howbeit, to finish my tale before the apples burn." He glanced significantly at the row of scorching Jonathans which Mehitable promptly turned. "One day little Mary appeared with drooping face. *My head doth ache!' quoth she, and she coughed, though it was a clear, warm day.

"Her mother bundled her down the ship's cabin, but not before I had stolen a kiss, for by that time I loved little Mary as dearly as ten years can love eight years. Then it was announced that little Mary had the measles!\""""}
    ],
    'max_tokens': 3000,  # Request a longer response
    'temperature': 0,  # Control the randomness of the response
    'top_p': 0,  # Control the diversity of the response
}

response = requests.post(endpoint, json=data, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print('Failed to fetch data:', response.status_code, response.text)
