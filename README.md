# Data Extraction from 'Open Weather map' API and Storage into BIGQUERY

## Project Overview :
This project consists of extracting weather datas of specific cities upon API calls. The extracted data must be then stored within a file before being loaded in a Database. 

Here I am going to extract data from Netherlands weather stations with [OPEN WEATHER MAP](https://openweathermap.org/api) data files. After extraction, I will structure the data (csv format) with Apache Airflow task orchestration with PythonOperator and BashOperator, then the data will be stored in in a Google Cloud Storage Bucket before loading it to Bigquery.

### Hereafter the steps that i will follow :

1 - GCP Project Creation : 
First of all, i created a new GCP project and enabled BigQuery and API Gateway APIS.

2 - Static Ressources Creation via Terraform : 
To make it more interesting, i decided to create all the static ressources (GCS buckets, roles, service accounts and Datasets) using Terraform. Please find below the link to my Terraform repo :

3 - Orchestrator Deployment : 
I will display two ways to Deploy an Airflow Orchestrator using both CLI (Cloud Console) and the UI.

4 - Dag Creation :
Once all the infrastracture is set, I will proceed with the DAG Creation that will perfom the extraction job.

5 - Testing : 
Finally, i will perform some tests a provide proof of the concept.




## I - GCP Project Creation
To create a Google Cloud project:

1- In the Google Cloud console, go to Menu menu > IAM & Admin > Create a Project.
Go to Create a Project
![image](https://user-images.githubusercontent.com/68516240/198010752-84fa77e2-d395-4515-b00d-ca2a82159496.png)

2 - In the Project Name field, enter a descriptive name for your project.
3 - In the Location field, click Browse to display potential locations for your project. Then, click Select.
4 - Click Create.

<img width="500" alt="image" src="https://user-images.githubusercontent.com/68516240/198011439-39723366-f8ec-4d07-bfc2-772df752ae56.png">

Now, Our Google Cloud Project is set and ready for ressources deployment.




## II - Static Ressources Creation via Terraform

First of all, I will start by manually creating a Service Account with Editor role for Terraform to be able to create Ressources on our GCP project.

<img width="791" alt="image" src="https://user-images.githubusercontent.com/68516240/198012944-955d3315-e148-4320-b00d-6c3f5c70d6fa.png">

<img width="1193" alt="image" src="https://user-images.githubusercontent.com/68516240/198013173-a0def5b1-07a7-4f46-91bf-def06050d7ea.png">

The following step is to Enable all services APIS that will be used in our project : 

<img width="608" alt="image" src="https://user-images.githubusercontent.com/68516240/198023299-f06d736a-57ff-417a-adcd-f71863637c35.png">
<img width="608" alt="image" src="https://user-images.githubusercontent.com/68516240/198023378-b918efb4-8a97-4b35-bb4e-527ec71bfa56.png">
<img width="608" alt="image" src="https://user-images.githubusercontent.com/68516240/198023634-5147becc-fbdb-4ff4-b330-461364c6b30c.png">
<img width="608" alt="image" src="https://user-images.githubusercontent.com/68516240/198023929-a98eb1e5-9957-480a-b392-14d7a6d1c08c.png">

The 'Terraform apply' went smoothly, and 9 Ressources à planned for deployment.

Then the next step is to 'Terraform apply' the static ressource created in the other repository.
![image](https://user-images.githubusercontent.com/68516240/198025087-00f7330c-b2be-4818-b08d-dfa58bee6c75.png)

![image](https://user-images.githubusercontent.com/68516240/198027004-75f61d97-bbcd-4e87-be3c-2ccb755ed18c.png)



## III - Airflow Orchestrator Deployment : 

#### Airflow environment creation via gcloud CLI :

To keep it simple, I will create an Airflow env with a basic setup.
To do so, i run the following command in the cloud shell :

`gcloud composer environments create ar-composer-environment \
      --location europe-west1 \
      --image-version composer-2.0.29-airflow-2.2.5`



#### Airflow environment creation via UI :

In Composer service, select **CREATE ENVIRONMENT** > **Composer 2**
![image](https://user-images.githubusercontent.com/68516240/198031970-ae0bfc46-ef19-4f72-bede-f58dc513dba2.png)
