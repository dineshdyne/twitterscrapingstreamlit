import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import plotly.graph_objects as go
import plotly.express as px
import hydralit_components as hc
# import hydralit as hy
from streamlit.scriptrunner.script_run_context import get_script_run_ctx
import streamlit as st
import snscrape.modules.twitter as sntwitter
import snscrape.modules.facebook as snfb
import snscrape.modules.instagram as sninsta
from PIL import Image
from itertools import *
from more_itertools import *
import streamlit_authenticator as stauth
# import joblib
# import dill
import streamlit.components.v1 as components

st.set_page_config(  # Alternate names: setup_page, page, layout
    # Can be "centered" or "wide". In the future also "dashboard", etc.
    layout="wide",
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    # String or None. Strings get appended with "• Streamlit".
    page_title=f"Social Media Scraping",
    page_icon=None,  # String, anything supported by st.image, or None.
)
image = Image.open("images/tvs-logo.png")
st.sidebar.image(image, use_column_width=False)
st.sidebar.title(f"Social Media Scraping")


names = ["Admin", "User", "test", ]
usernames = ["admin", "user", "test"]
passwords = ["123", "456", "789"]

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "user_cookie",
    "user_signature",
    cookie_expiry_days=30,
)

name, authentication_status, username = authenticator.login("Login", "main")


if authentication_status:
    st.info(f"Logged in as {name}")
    site=st.sidebar.selectbox("Select Site", ["Twitter", "Facebook", "Instagram"])
    if site=="Twitter":
        st.sidebar.subheader("Twitter")
        st.sidebar.markdown("""
        [Twitter](https://twitter.com) is a social networking service that enables users to send and read short 280-character messages called **tweets**.
        """)
        st.sidebar.markdown("""
        [Twitter API](https://developer.twitter.com/en/docs/basics/twitter-ids) is a REST API that allows you to access Twitter data.
        """)
        st.sidebar.markdown("""
        [Twitter Dev](https://developer.twitter.com/en/docs/basics/twitter-ids) is a website that provides a list of Twitter API endpoints.
        """)
        st.sidebar.markdown("""
        [Twitter Advance Search](https://github.com/igorbrigadir/twitter-advanced-search) Readme file for twitter advanced search query filters.
        """)

        search_terms = st.selectbox("Search Terms", ['user','download posts','trends'])
        # tweet_count = st.number_input("Number of Tweets", min_value=1, max_value=100, value=10)
        
        if search_terms=='user':
            user_name = st.text_input("User Name")
            try:
                userScraper = sntwitter.TwitterProfileScraper(user_name)
                st.subheader("User Data")
                userdata = dict(json.loads(userScraper._get_entity().json()))
                
                                    #can apply customisation to almost all the properties of the card, including the progress bar
                theme_bad = {'bgcolor': '#FFF0F0','title_text_align':'center','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
                theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
                theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
                
                st.markdown(f"""<div style="background-color:#377ed4;padding:25px;border-radius:10px;"><p>Username:{userdata['username']} </p>
                            <p>Display Name: {userdata['displayname']}</p>
                            <p>Description : {userdata['description']}</p>
                            <p>Created Date: {userdata['created']} </p>
                            </div>""",unsafe_allow_html=True)
                st.write(f"""Twitter Page: [Twitter Link]({userdata['url']})""")
                
                
                cc = st.columns(3)
                with cc[0]:
                # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
                    hc.info_card(title='Follower Count', content=userdata['followersCount'], sentiment='good',bar_value=77,)
                    hc.info_card(title='Listed', content=userdata['listedCount'],bar_value=12,sentiment='good')#theme_override=theme_good)
                    
                with cc[1]:
                    hc.info_card(title='Following', content=userdata['friendsCount'],bar_value=12,theme_override=theme_bad)
                    hc.info_card(title='Favourites Count', content=userdata['favouritesCount'], sentiment='bad',bar_value=77,)
                    

                with cc[2]:
                    hc.info_card(title='Posts', content=userdata['statusesCount'], sentiment='neutral',bar_value=55)
                    hc.info_card(title='Media', content=userdata['mediaCount'], sentiment='neutral',bar_value=55)

                # with cc[3]:
                # #customise the the theming for a neutral content
                #     hc.info_card(title='Some NEUTRAL',content='Maybe...',key='sec',bar_value=5,theme_override=theme_neutral)
                # st.write(user_data)
            except:
                st.error("Details not found")
        elif search_terms=='download posts':
            with st.form("Query tweets"):
                col1,col2=st.columns(2)
                query_type=col1.selectbox('Select query type',options=['User Posts','Hastag','quote'])
                query = col2.text_input("Input query")

                col1,col2,col3=st.columns(3)
                max_tweets=col1.number_input("Input maximum number of tweets",min_value=1,max_value=500,value=10)
                min_date=col2.date_input("Input Start Date")
                max_date=col3.date_input("Input End Date")
                #st.write(min_date,max_date)
                submitted=st.form_submit_button("Submit")
            if submitted:
                try:
                    func_map={'User Posts':sntwitter.TwitterUserScraper,
                            'Hastag':sntwitter.TwitterHashtagScraper,
                            'quote':sntwitter.TwitterSearchScraper}
                    tweet_list=[]
                    
                    connect=func_map[query_type](query)#+"since:2020-06-01 until:2020-07-31")
                    for i,tweet in enumerate(connect.get_items()):
                        if i>=max_tweets:
                            break
                        tweet_list.append([tweet.id,tweet.date,tweet.user.username,tweet.content,tweet.likeCount])
                        
                    tweet_df=pd.DataFrame(tweet_list,columns=['id','timestamp','user','tweet','likes'])
                    st.dataframe(tweet_df)
                except:
                    st.error("Details not found")
        
        elif search_terms=='trends':
            trends = sntwitter.TwitterTrendsScraper()
            trend_list=[]
            for i,tweet in enumerate(trends.get_items()):
                trend_list.append([tweet.name,tweet.domainContext,tweet.metaDescription])
                        
            tweet_df=pd.DataFrame(trend_list,columns=['Trend','Context','Popularity'])
            st.subheader("Trends Data")
            st.table(tweet_df)
        


    elif site=="Facebook":
        st.sidebar.subheader("Facebook")
        st.sidebar.markdown("""
        [Facebook](https://www.facebook.com) is a social networking service that enables users to share content and interact with friends and family.
        """)
        st.sidebar.markdown("""
        [Facebook API](https://developers.facebook.com/docs/graph-api) is a REST API that allows you to access Facebook data.
        """)
        st.sidebar.markdown("""
        [Facebook Dev](https://developers.facebook.com/docs/graph-api) is a website that provides a list of Facebook API endpoints.
        """)
    elif site=="Instagram":
        st.sidebar.subheader("Instagram")
        st.sidebar.markdown("""
        [Instagram](https://www.instagram.com) is a social networking service that enables users to share pictures and videos, and interact with other users on the platform.
        """)
        st.sidebar.markdown("""
        [Instagram API](https://www.instagram.com/developer/endpoints/users/) is a REST API that allows you to access Instagram data.
        """)
        st.sidebar.markdown("""
        [Instagram Dev](https://www.instagram.com/developer/endpoints/users/) is a website that provides a list of Instagram API endpoints.
        """)

elif username:

    st.error("Login Error - Check Username and Password")
else:
    st.info("Input Username")
    