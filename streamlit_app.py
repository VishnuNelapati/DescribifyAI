import streamlit as st
from openai import OpenAI
from utils import initial_messages
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

st.set_page_config(page_title="DescribifyAI",page_icon=":robot_face:")

selection = st.selectbox("What option would you like to try ?" ,['Prompt','Image'])

open_api_client = OpenAI(api_key=st.secrets['open_api_key'])

if selection == "Prompt":

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


if selection == "Image":

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

                    expected_format = '''{"nutritionFacts":[{
                                                    "nutritionName": "nutritionName",
                                                    "percentage": "%",
                                                    "quantity": "",
                                                    "measure": ""
                                                },
                                                "serving":{"servingSize":"" , "Calories":""}]}'''
                    
                    extra_info = "Provide any additional deatils or specifications at the end"

                    question = "Generate nutritional details or specification here using above OCR outptut in specified format.If no nutrition information is found in the image , please provide details of the OCR text in JSON format."


                    m=f"{ocr_output} \n\n Generate nutritional details or specification here using above OCR outptut in below specified format \n\n {expected_format} \n\n {extra_info} \n\n If no nutrition information is found in the image , please provide details of the OCR text in JSON format like product name or brands or serving size or Calories per serving etc.If the product is not a edible item , then do not provide any info of serving size or calories. \n\n"

                                    
                    nutrition_response = open_api_client.chat.completions.create(
                            model = "gpt-3.5-turbo-1106",
                                    messages=[{"role":"user","content":m}],
                                    max_tokens=1000,
                                    temperature=0
                        )

                    # st.write(nutrition_response.choices[0].message.content)

                    st.code(nutrition_response.choices[0].message.content,language="python")                    

