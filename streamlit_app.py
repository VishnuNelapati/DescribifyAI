import streamlit as st
from openai import OpenAI
from utils import initial_messages
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

st.set_page_config(page_title="DescribifyAI",page_icon=":robot_face:")

st.title("Product Information Application")

st.header("Problem Statement")
st.markdown("""
        In the fast-paced realm of e-commerce, maintaining an accurate and informative product catalog is crucial for businesses. 
        However, challenges arise when integrating new products into the catalog, especially when upstream data sources do not 
        provide comprehensive product descriptions or nutrition information or other required information. This lack of detailed information hinders the effective showcasing of 
        products on websites, leading to potential customer disengagement.
    """)
st.markdown("""
        Traditionally, the solution involves reaching out to vendors or business partners to obtain missing product details or requesting them to update the product information. 
        This manual process often results in delays, back-and-forth communication, and may impact the overall efficiency of 
        updating product listings. Our web application addresses this challenge by offering an automated solution for 
        generating product descriptions using advanced language models, reducing the dependency on external sources.
    """)
st.header("Solution")
st.markdown("""
    Our web application provides a comprehensive solution to the challenges posed by incomplete product information. 
    Leveraging the capabilities of OpenAI GPT-3.5, we empower store managers to generate dynamic product descriptions 
    with ease. By inputting product titles and brand prompts, GPT-3.5 generates engaging and informative product descriptions 
    on-demand. This eliminates the need for manual intervention and accelerates the process of enriching product data 
    for seamless display on webpages.
""")
st.markdown("""
    Additionally, our application caters to the specific use case where store managers can upload images from various 
    angles directly into database. These images, taken from different perspectives within the store, serve as inputs 
    to our image analysis model. The integration of Azure Cognitive Services, particularly Optical Character Recognition (OCR), 
    enables the extraction of essential details such as product titles, brands, nutrition information, and more. This automated 
    process significantly reduces the workload on store managers, ensuring accurate and efficient extraction of product attributes.
""")
st.markdown("""
    By combining the power of advanced language models and image analysis, our web application not only streamlines the 
    generation of product descriptions but also enhances the efficiency of acquiring and updating product attributes. 
    Store managers can effortlessly upload images from all angles, facilitating a robust approach to maintaining an 
    up-to-date and informative product catalog.
""")

st.markdown("---")

st.markdown("Currenlty we have two different approaches to get the product infomation.Please choose one of the tabs from below to experiment with.")

# selection = st.selectbox("What option would you like to try ?" ,['Prompt','Image'])

selection = st.radio(horizontal=True,label="Select One",options=['Product Description - Prompt','Product Attributes - Image'],)

open_api_client = OpenAI(api_key=st.secrets['open_api_key'])

if selection == "Product Description - Prompt":

    st.title("DescribifyAI")

    deafult_welcome_message = "Hello , I am Describify AI Bot. How can i help you today ?"
    fine_tuned_model='ft:gpt-3.5-turbo-0613:personal:describify-ai:8mYIehvC'
    # fine_tuned_model = 'ft:gpt-3.5-turbo-0613:personal:describify-ai:8lqK4E95'

    if "messages" not in st.session_state.keys():
        st.session_state.messages=[]
        st.session_state["messages"].extend(initial_messages())
        st.session_state["messages"].append({"role":"assistant","content":deafult_welcome_message})

    for message in st.session_state.messages[2:]:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Create a box to enter user input and store it in user_promt variable
    user_prompt = st.chat_input("Say Something")

    if user_prompt:

        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state["messages"].append({"role":"user","content":user_prompt})

        # with st.spinner("generating response....."):

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in open_api_client.chat.completions.create(
                model = fine_tuned_model,
                        messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                        max_tokens=400,
                        temperature=0,stream=True
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response+"▌")
            
            message_placeholder.markdown(full_response)
        st.session_state["messages"].append({"role":"assistant","content":full_response})


    with st.expander("Addition details"):
        st.write(st.session_state.messages[2:])
        st.download_button("Download Conversation :arrow_down:",data=str(st.session_state.messages),file_name="conv.txt")


if selection == "Product Attributes - Image":

    # out = st.toggle(label="Json Format",)

    endpoint = st.secrets['azure_end_point']
    key = st.secrets['azure_api_key']

    input_images = st.file_uploader("Upload image(s) in supported formats",accept_multiple_files=True,type = ['jpeg','png','jpg'])

    client = ImageAnalysisClient(endpoint=endpoint,
                                credential=AzureKeyCredential(key))

    if input_images == []:
        pass
    else:

        for index,tab in enumerate(st.tabs([input_image.name for input_image in input_images])):
            
        # for index,img in enumerate(input_images):
            with tab:
                st.image(input_images[index])
                result = client.analyze(image_data=input_images[index],
                                        visual_features=[VisualFeatures.CAPTION,VisualFeatures.READ,VisualFeatures.DENSE_CAPTIONS,VisualFeatures.SMART_CROPS,VisualFeatures.TAGS],
                                        gender_neutral_caption=True)
                with st.expander("Json Details"):
                    # st.write(result.read)
                    # st.write(result.caption)

                    # st.write(result.dense_captions)
                    # st.write(result.smart_crops)
                    # st.write(result.tags)

                    ocr_output = f"{result.read}"

                    expected_format_dict = '''{"nutritionFacts":[{
                                                    "nutritionName": "nutritionName",
                                                    "percentage": "%",
                                                    "quantity": "",
                                                    "measure": ""
                                                }],
                                                "serving":{"servingSize":"" , "Calories":""},
                                                "Extra Info" : {"ProductName":"" , "Brand":"" ,"Description":"" , etc }
                    }'''

                    expected_format = ''' A table with nutritionName, percentage , quantity , measure as another columns. Add Serving size and calories details at the end of the table.If the value for any  nutrition name is 20mg , then Quantity should have 20 and measure should have unit i.e mg'''
                    
                    # if out:
                    #     expected_format = expected_format_dict
                    # else:
                    #     expected_format = expected_format_table

                    extra_info = "Provide any additional deatils or specifications at the end including product descriptions like product names , brand of the product , general info of the product using product name and brand etc based on the OCR data as bullet points or key value pairing. "
                    # "in below format Additional Details : \n Product name : '' ,\n Brand : '' ,\n Warnings : '' etc , Add additional attributes to additional details based on image information. "

                    question = "Generate nutritional details or specification here using above OCR outptut in specified format.If no nutrition information is found in the image , please provide details of the OCR text in JSON format."


                    m=f"{ocr_output}\n\n {result.caption}\n\n {result.dense_captions}\n\n {result.smart_crops} \n\n{result.tags} \n\n Generate nutritional details or specification here using above OCR outptut (contains OCR output , caption , tags , smartCrops,densecaptions etc) in below specified format \n\n {expected_format} \n\n {extra_info} \n\n If no nutrition information is found in the image , please provide details of the OCR text in JSON format like product name or brands or serving size or Calories per serving etc.If the product is not a edible item , then do not provide any info of serving size or calories.Try to formulate product descrition of the product based on above OCR outputs. \n\n"

                                    
                    nutrition_response = open_api_client.chat.completions.create(
                            model = "gpt-3.5-turbo-1106",
                                    messages=[{"role":"user","content":m}],
                                    max_tokens=1200,
                                    temperature=0
                        )

                    # st.write(nutrition_response.choices[0].message.content)

                    st.code(nutrition_response.choices[0].message.content,language="python")                    

