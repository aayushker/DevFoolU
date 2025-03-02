![DevFoolU](https://socialify.git.ci/aayushker/DevFoolU/image?description=1&name=1&owner=1&theme=Auto)

<div align="center" style="display: flex; flex-direction: column; align-items: center;">

[![Vercel Deploy](https://deploy-badge.vercel.app/vercel/devfoolu)](https://devfoolu.vercel.app)
![Render](https://img.shields.io/badge/Render-Deployed-green?logo=render)

</div>
DevFoolU is an automated plagiarism detection tool designed to maintain the integrity of hackathons by analyzing project submissions on Devfolio. It scans each new submission, compares it with existing projects, and identifies potential similarities or copied content to ensure originality and fair competition.

## Table of Contents

- [🔥 **Features**](#-features)
- [🖥️ **Technologies Used**](#️-technologies-used)
- [🚀 **Getting Started**](#-getting-started)
- [📚 **Challenges We Ran Into**](#-challenges-we-ran-into)
- [📝 **Future Enhancements**](#-future-enhancements)
- [📄 **License**](#-license)
- [🤝 **Acknowledgments**](#-acknowledgments)

<br />

## 🔥 **Features**

- **Automated Plagiarism Detection**: Compares new submissions with past projects to detect similarities.
- **Efficient Scalability**: Handles large volumes of data, enabling quick comparisons across thousands of projects.
- **Tech-Stack Flexibility**: Supports a variety of technologies including Python, NLP, and web scraping tools.
- **Fair Competition**: Ensures hackathons remain focused on fostering genuine innovation and creativity.
- **Real-Time Scanning**: Scans projects upon submission, providing instant feedback to organizers and participants.
- **Customizable Similarity Threshold**: Allows organizers to adjust sensitivity to false positives and negatives.
  <br />

## 🖥️ **Technologies Used**

- **Backend**: Django Rest Framework (Python), CSV
- **Frontend**: Next.js, Typescript, NextUI, ShadCN, Tailwind CSS
- **Framework & Library**: Hugging Face Transformers, Selenium, Pandas, Scikit-learn, KeyBERT, NLTK
- **API Communication**: Axios
- **Deployment**: Vercel, Docker, Render

<br />

## 🚀 **Getting Started**

### Prerequisites

Ensure you have the following installed:

- **Python**
- **Pipenv**
- **Node.js**
- **NPM**

## Installation

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aayushker/DevFoolU.git
   cd DevFoolU/backend
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
   ```
4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```
2. **Install dependencies:**
   ```bash
    npm install
   ```
3. **Run the development server:**
   ```bash
   npm run dev
   ```

<br />

## Challenges We Ran Into

### 1. Handling Large-Scale Data

- **Hurdle**: With over 180,000 projects on DevFoolU, managing and comparing such a large dataset posed performance challenges.
- **Solution**: We optimized data storage and comparison processes, using efficient indexing and caching mechanisms to improve performance.

### 2. Dynamic Content Parsing and Scraping

- **Hurdle**: DevFoolU project pages are dynamically rendered, which made scraping the project data tricky.
- **Solution**: We used tools like Selenium and BeautifulSoup with smart fallback mechanisms to adapt to changing page structures and dynamically load content.

### 3. Textual Crux Extraction and Vectorization

- **Hurdle**: Summarizing project descriptions into a concise "crux" for comparison was challenging due to varying lengths and formats.
- **Solution**: We implemented NLP models to extract key phrases and summarize descriptions, enabling accurate vectorization and faster comparisons.

### 4. Ensuring Accuracy in Similarity Detection

- **Hurdle**: Finding the right balance between false positives and negatives was difficult.
- **Solution**: We refined similarity thresholds using feedback from multiple test runs, optimizing the detection algorithms to strike a balance between speed and accuracy.
  <br />

## 📝 **Future Enhancements**

### 1. Enhanced Similarity Detection

- **Goal**: Improve the accuracy and efficiency of plagiarism detection using advanced Natural Language Processing (NLP) models and machine learning algorithms.
- **Plan**: Implement techniques like **semantic similarity** (e.g., BERT, GPT models) to better understand the context of project descriptions and reduce false positives.
- **Impact**: Higher accuracy in detecting truly similar projects, even those with paraphrased descriptions or code snippets.

### 2. Real-Time Plagiarism Detection

- **Goal**: Enable real-time project comparisons as new submissions are added to DevFoolU.
- **Plan**: Integrate real-time scraping and similarity checking via a webhook system or automated API calls as new projects are uploaded.
- **Impact**: Instant feedback for hackathon participants, reducing manual verification time and increasing event efficiency.

### 3. Visual Similarity Detection (Code Comparison)

- **Goal**: Expand plagiarism detection to include visual code structure and not just textual content.
- **Plan**: Utilize AI-driven code analysis tools like **CodeBERT** or other similar models to compare submitted code for structural similarity, variable names, and algorithms.
- **Impact**: A more robust system that can detect plagiarism in both code and documentation, ensuring the integrity of the projects on a deeper level.

### 4. User Feedback and Iteration

- **Goal**: Continuously improve the tool based on user feedback from hackathon participants and organizers.
- **Plan**: Implement feedback loops where users can report inaccuracies or issues, which will help improve the system’s performance.
- **Impact**: A more user-centric tool, continuously improving its accuracy and usability.

### 5. Cross-Platform Integration

- **Goal**: Expand the plagiarism detection tool to other hackathon platforms like **Devpost**, **Hackerearth**, and **Kaggle**.
- **Plan**: Build integrations with other project-hosting platforms and extend the database to include submissions from these sites.
- **Impact**: Wider usage across different communities, enhancing the tool's value and adoption.

### 6. Reporting and Analytics Dashboard

- **Goal**: Provide detailed analytics and reporting for hackathon organizers and participants.
- **Plan**: Create a dashboard where organizers can see trends in project originality, track similarity scores, and generate detailed reports.
- **Impact**: Better insights for hackathon organizers to maintain fairness, and an additional layer of transparency for participants.

### 7. Open Source Collaboration

- **Goal**: Make the project open-source, allowing other developers to contribute and improve the tool.
- **Plan**: Publish the source code on platforms like GitHub and encourage collaboration through issues, pull requests, and discussions.
- **Impact**: Leverage the open-source community for rapid innovation and feature development.

### 8. Gamification of the Originality Process

- **Goal**: Encourage developers to submit unique and original projects through gamification.
- **Plan**: Introduce rewards, leaderboards, or badges for participants with high originality scores based on the plagiarism detection results.
- **Impact**: Increased motivation for participants to submit more creative and authentic projects.

## Conclusion

By evolving DevFoolU with these future aspects, we aim to create a comprehensive and indispensable tool for hackathon organizers and participants, ensuring the integrity and fairness of every project submission.

<br />

## 📄 **License**

This project is licensed under the GNU General Public License. See the `LICENSE` file for more details.
