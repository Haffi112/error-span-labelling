# **Specification Document: Translation Error Span Annotation Interface**

## **1. Overview**
This document outlines the specifications for a web-based labeling interface designed to facilitate the Error Span Annotation (ESA) method for evaluating machine translations. The interface will allow annotators to rate three machine-translated sentences at a time, marking error spans and providing overall scores.

## **2. Core Features**

### **2.1 Annotation Task**
* Display three machine-translated sentences simultaneously.
* Allow annotators to select text spans within each sentence.
* Enable marking of selected spans as minor or major errors.
* Provide functionality to indicate missing content as minor or major concerns.
* Include an overall score input (0-100%) for each sentence. The text on the score input should say “0 % no meaning preserved, 33 % some meaning preserved, 66 % most meaning preserved, 100 % perfect”.
* All annotators see the tasks in the same order.
* It's also helpful to be able to go back to examples and look through the annotations you already made before you decide that you are done with everything. Sometimes we make mistakes, so it's important that we can fix them.

### **2.2 Task Management**
* Randomize the order of presented sentences to prevent bias.
* Display a progress bar showing the number of completed and remaining examples.
* Automatically present the next unannotated example upon task completion.
* Assign a unique ID to each set of three sentences for easy navigation and sharing.

### **2.3 Admin Features**
* Provide an interface for admins to upload CSV files containing sentences for annotation.
* Automatically create annotation tasks from uploaded CSV data.

## **3. Technical Specifications**

### **3.1 Backend**
* Framework: Flask (Python)
* Database: PostgreSQL (for storing sentences, annotations, and user data)
* Deployment: Heroku

### **3.2 Frontend**
* Framework: Templates in Flask
* UI Components: DaisyUI
* Responsive design for various screen sizes


## **4. User Interface**

### **4.1 Annotator View**
* Login screen
* Main annotation interface:
    * Progress bar at the top
    * Three sentences displayed side by side
    * Text selection tool for marking error spans
    * Buttons for classifying errors as minor or major
    * Interface for marking missing content
    * Overall score input (0-100%) for each sentence
    * Submit button to complete the current annotation and move to the next unannotated example
    * URL with unique ID for the current set of sentences

### **4.2 Admin View**
* Login screen with admin privileges
* Dashboard showing annotation progress
* CSV upload interface
* Task management screen (create, edit, delete tasks)


## **5. Data Model**

Use SQLAlchemy for the database model and flask migrations.

### **5.1 Sentences**
* ID
* Original text
* Translation method
* Source language
* Target language


### **5.2 Annotations**
* ID
* Sentence set ID
* Annotator ID
* Error spans (start index, end index, error type)
* Missing content markers
* Overall score
* Timestamp


### **5.3 Users**
* ID
* Username
* Password (hashed)
* Role (Annotator/Admin)
* Last annotated set ID


## **6. Workflow**
1. Admin uploads CSV file with sentences.
2. System creates annotation tasks from the uploaded data.
3. Annotator logs in and is automatically directed to their next unannotated example.
4. The URL updates to include the unique ID of the current sentence set.
5. Annotator performs the following for each sentence: a. Selects text spans and classifies them as minor or major errors. b. Mark missing content as minor or major concerns. c. Provides an overall score (0-100%).
6. Annotator submits the annotation for the current set.
7. System automatically loads the next unannotated example.
8. Progress bar updates after each completed set.
9. Process continues until all assigned tasks are completed.


## **7. Navigation and URL Structure**
* Each set of three sentences will have a unique ID.
* The URL will include this ID: `/annotate/&lt;set_id>`
* When an annotator logs in, they will be redirected to their next unannotated example.
* Annotators can share or bookmark specific examples using the URL.
* If an annotator manually enters a URL with a set ID:
    * If it's unannotated, they can annotate it.
    * If it's already annotated (by them or someone else), they can view it in read-only mode.


## **8. Security Considerations**
* Implement secure user authentication and authorization.
* Ensure data encryption in transit and at rest.
* Regularly backup the database.
* Implement rate limiting to prevent abuse of the URL-based navigation.


## **9. Future Enhancements**
* Implement inter-annotator agreement calculations.
* Add a quality control mechanism to ensure annotation consistency.
* Develop an API for programmatic access to the annotation data.
* Create an admin interface for managing user progress and reassigning tasks if needed.


## **10. Performance Requirements**
* The application should support multiple concurrent users.
* Page load times should be under 2 seconds.
* Database queries should be optimized for quick retrieval of annotation tasks.
* Efficient algorithm for finding the next unannotated example for each user.

This updated specification addresses the navigation issues and improves the efficiency of the annotation process. It ensures that annotators always see the next unannotated example upon login or task completion, and provides a URL-based system for easy navigation and sharing of specific annotation tasks.
