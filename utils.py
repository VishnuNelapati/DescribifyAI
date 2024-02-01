def initial_messages():
    messages = [{"role": "system", "content": "You are a helpful AI Bot. Who generates products description for products based on the promt which contains product tilte and it's brand. Please make sure to add disclaimer or warnings where ever necessary."},
            {"role": "user", "content": "I have few products with product titles and brands, i want to generate product description for those products."}]
    
    return messages