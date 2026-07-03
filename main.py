import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import psycopg2
matplotlib.use("Agg")


conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"],
    port=st.secrets["DB_PORT"]
)

c = conn.cursor()
def create_table():
    c.execute("""
        CREATE TABLE IF NOT EXISTS blogtable(
            author TEXT,
            title TEXT,
            article TEXT,
            postdate DATE
        )
    """)
    conn.commit()


def add_data(author, title, article, postdate):
    c.execute(
        """
        INSERT INTO blogtable(author,title,article,postdate)
        VALUES (%s,%s,%s,%s)
        """,
        (author, title, article, postdate)
    )
    conn.commit()


def view_all_notes():
    c.execute("SELECT * FROM blogtable")
    return c.fetchall()


def view_all_titles():
    c.execute("SELECT DISTINCT title FROM blogtable")
    return c.fetchall()


def get_blog_by_title(title):
    c.execute(
        "SELECT * FROM blogtable WHERE title=%s",
        (title,)
    )
    return c.fetchall()


def get_blog_by_author(author):
    c.execute(
        "SELECT * FROM blogtable WHERE author=%s",
        (author,)
    )
    return c.fetchall()


def delete_data(title):
    c.execute(
        "DELETE FROM blogtable WHERE title=%s",
        (title,)
    )
    conn.commit()


title_temp = """
<div style="
    background-color:#464e5f;
    padding:15px;
    margin:10px auto;
    border-radius:10px;
    width:60%;
">

<h3 style="color:white;text-align:center;">{}</h3>

<div style="display:flex;align-items:center;gap:15px;">
<img src="https://www.w3schools.com/howto/img_avatar.png" style="width:50px;height:50px;border-radius:50%;">

<p style="color:white;font-size:24px;font-weight:bold;margin:0; margin-left:30px; text-align:center;">Author: {}</p>
</div>

<p style="color:white;margin-top:20px; margin-left:5px; text-align:center;">{}</p>

<h6 style="color:white;text-align:center;">Post Date: {}</h6>

</div>
"""

message_temp = """
<p style="background-color: text-align:center; border-radius: 10px; #F0F2F6; color:gray;font-size:15px;margin-top:20px; line-height:1.7;">Message :  {}</p>
"""

header_temp = """
<div style="
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    padding: 25px;
    margin: 20px auto;
    border-radius: 16px;
    width: 65%;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.08);
">

<h3 style="
    color: #e94560;
    text-align: center;
    margin-bottom: 20px;
    font-size: 22px;
    letter-spacing: 1px;
">{}</h3>

<hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:15px 0;">
<p style="
    color: #495670;
    text-align: right;
    font-size: 12px;
    margin-top: 20px;
    margin-bottom: 0;
">📅 {}</p>

</div>
"""

def main():
    create_table()      
    st.title("My blogs")
     
    menu = ["Home","View Posts","Add Post","Search","Mange"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Home":
        st.subheader("Home")
         
        result = view_all_notes()
        for i in result:
            b_author = i[0]
            b_title = i[1]
            b_article = str(i[2])[0:30]
            b_postdate = i[3]

            st.markdown(
                title_temp.format(
                    b_title,
                    b_author,
                    b_article,
                    b_postdate
                ),
                unsafe_allow_html=True
            )

    
    elif choice == "View Posts":
        st.subheader("View Articles")
        all_titles = [i[0] for i in view_all_titles()]
        postlist = st.sidebar.selectbox("View Post",all_titles)
        post_result = get_blog_by_title(postlist)
        for i in post_result:
            b_author = i[0]
            b_title = i[1]
            b_article = i[2]
            b_postdate = i[3]

            st.markdown(
                header_temp.format(
                    b_author,
                    b_postdate
                ),
                unsafe_allow_html=True
            )
            st.markdown(message_temp.format(b_article),unsafe_allow_html=True)
       
    
    elif choice == "Add Post":
        st.subheader("Add Articles")
        create_table()
        blog_author = st.text_input("Enter your name",max_chars=50)
        blog_title = st.text_input("Enter post title")
        blog_article = st.text_area("Enter Articles",height=300)
        blog_post_date = st.date_input("Date")
        if st.button("Add"):
            add_data(blog_author,blog_title,blog_article,blog_post_date)
            st.success("Post: {} saved".format(blog_title))


    
    elif choice == "Search":
        st.subheader("Search Articles")
        search_term = st.text_input("Enter Search Term")
        search_choice = st.radio("Filed to search by",("title","author"))
        if st.button("Search"):
        
            if search_choice=="title":
                article_result = get_blog_by_title(search_term)
            elif search_choice=="author":
                article_result = get_blog_by_author(search_term)

            for i in article_result:
                b_author = i[0]
                b_title = i[1]
                b_article = i[2]
                b_postdate = i[3]

                st.markdown(
                    header_temp.format(
                        b_author,
                        b_postdate
                    ),
                    unsafe_allow_html=True
                )
                st.markdown(message_temp.format(b_article),unsafe_allow_html=True)
        
    elif choice == "Mange":
        st.subheader("Mange Articles")
        result = view_all_notes()
        clean_db = pd.DataFrame(result,columns=["Author","Title","Articles","Post date"])
        st.dataframe(clean_db)
        unique_titles = [i[0] for i in view_all_titles()]
        delete_blog_by_title = st.selectbox("Unique title",unique_titles)
        if st.button("Delete"):
            delete_data(delete_blog_by_title)
            st.warning("Deleted :'{}'".format(delete_blog_by_title))


        if st.checkbox("Matrics"):
            new_df = clean_db
            new_df['Length'] = new_df['Articles'].str.len()
            st.dataframe(new_df)

            fig, ax = plt.subplots()
            new_df["Author"].value_counts().plot(
                kind="bar",
                ax=ax
            )
            st.pyplot(fig)
            st.subheader("Author Stats (Pie Chart)")
            fig, ax = plt.subplots()
            new_df["Author"].value_counts().plot.pie(
                autopct="%1.1f%%",
                ax=ax
            )
            ax.set_ylabel("")
            st.pyplot(fig)



if __name__ == "__main__":
    main()