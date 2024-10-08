import requests
import streamlit as st

from PIL import Image

st.set_page_config(page_title="My Webpage", page_icon=":tada:", layout="wide")

st.title(":blue[Autism Spectrum Disorder]")
st.write("---")
with st.container():
    col1,col2= st.columns([3,2])
    with col1:
        st.title("What is Autism Spectrum Disorder?")
        st.write("""
        Autism spectrum disorder (ASD) is a developmental disability caused by differences in the brain. People with ASD often have problems with social communication and interaction, and restricted or repetitive behaviors or interests. People with ASD may also have different ways of learning, moving, or paying attention.
        """)
    with col2:
        img1=Image.open("image/asd_child.jpg")
        st.image(img1,width=300)


with st.container():
    col1,col2= st.columns([4,2])
    with col1:
        st.title("What Causes Autism Spectrum Disorder?")
        st.write("""
        The Autism Spectrum Disorder Foundation lists the following as possible causes of ASD:

        :blue[Genetics] : Research suggests that ASD can be caused by a combination of genetic and environmental factors. Some genes have been identified as being associated with an increased risk for ASD, but no single gene has been proven to cause ASD.
        
        :blue[Environmental factors] : Studies are currently underway to explore whether certain exposure to toxins during pregnancy or after birth can increase the risk for developing ASD.
        
        :blue[Brain differences] : Differences in certain areas of the brain have been observed in people with ASD, compared to those without ASD. It is not yet known what causes these differences.
        """)
    with col2:
        img1=Image.open("image/causes-of-autism.png")
        st.image(img1,width=350, caption="Causes of ASD")


with st.container():
    col1,col2= st.columns([4,2])
    with col1:
        st.title("Symptoms of ASD:")
    
        st.write("""
        1. Avoids or does not keep eye contact
        2. Does not respond to name by 9 months of age
        3. Does not show facial expressions like happy, sad, angry, and surprised by 9 months of age
        4. Lines up toys or other objects and gets upset when order is changed
        5. Repeats words or phrases over and over (called echolalia)
        6. Plays with toys the same way every time
        7. Delayed language skills
        8. Delayed movement skills
        9. Delayed cognitive or learning skills
        10. Hyperactive, impulsive, and/or inattentive behavior
        11. Epilepsy or seizure disorder
        12. Unusual eating and sleeping habits
        13. Gastrointestinal issues (for example, constipation)
        14. Unusual mood or emotional reactions
        15. Anxiety, stress, or excessive worry
        16. Lack of fear or more fear than expected, etc.
        """)
        st.write("[Learn More >](https://www.who.int/news-room/fact-sheets/detail/autism-spectrum-disorders)")
    with col2:
        img=Image.open("image/autism.png")
        st.image(img,caption="Signs of ASD")
        img1=Image.open("image/Strategies.jpeg")
        st.image(img1,caption="")
    


# ---- WHAT I DO ----
with st.container():

    left_column, right_column = st.columns([4,2])
    with left_column:
        st.title("Prevalence Autism in Malaysia ")
        
        st.write("""
            The exact prevalence of Autism Spectrum Disorder (ASD) in Malaysia is not well-established due to a lack of nationwide studies and consistent diagnostic criteria. However, some studies have estimated that the prevalence of ASD in Malaysia is between 1 and 2 per 1000 children.
            According to to an Ministry of Health (MOH) study in 2005, which use modified checklist for Autism in Toddlers (M-CHAT) screener for ASD, the prevelance in Malaysia is between one and two per 1000 children aged 18 months to three years. The study also found that male children are four times more likely to get ASD than female children.  
            
            • Prevalence of Autism: Between 1 in 500 (2/1,000) to 1 in 166 children (6/1,000) have an Autism Spectrum Disorder (Center for Disease Control).
            
            • The number of children in Sibu, Sarawak diagnosed of being ASD is higher than international average.
            
            • Sibu Autistic Association (SAA) president David Ngu said 70 children were identified with ASD every year in town, or one in every 68 newborn.
            
            • Autism is four times more prevalent in boys than girls in the US (Autism Society of America).
            
            • Autism is more common than Down Syndrome, which occurs in 1 out of 800 births.
            
            • Prevalence of autism is expected to reach 4 million people in the next decade in the US (Autism Society of America).
                 
            • Ninety percent of autistic children are only identified as such by their parents after the age of two.
            """)

    with right_column:
        img=Image.open("image/autism-stats-1.jpg")
        st.image(img,width=350,caption="ASD ststistics")
        img1=Image.open("image/autism-stats-2.png")
        st.image(img1,width=350,caption="USA data over 18 years")

with st.container():
    st.title("World Autism Awareness Day")
    st.write(
        "This year, WAAD will be observed with a virtual event on Sunday, 2 April, from 10:00 a.m. to 1:00 p.m. EDT.The event is organized in close collaboration with autistic people and will feature autistic people from around the world discussing how the transformation in the narrative around neurodiversity can continue to be furthered in order to overcome barriers and improve the lives of autistic people. It will also address the contributions that autistic people make – and can make – to society, and to the achievement of the Sustainable Development Goals."
    )
c1,c2=st.columns([5,5])
im=Image.open("image/World.png")
c1.image(im,caption="")
im1=Image.open("image/Worlds.png")
   
c2.image(im1,caption="")
        