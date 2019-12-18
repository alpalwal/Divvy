# Formatter to take the DivvyCloud compliance scorecard insight findings and make sure each insight violation has its own row. 
# Steps:
'''
1. Download your desired DivvyCloud Compliance Scorecard
2. Delete all tabs besides "Impacted Resources"
3. Save the file as company_csv_unformatted.csv and put it in the same folder you'll be running the python script from. (you can change the name of the file in the script without any issue)
4. Run the script. (python scorecard_formatter.py)
5a. If the script worked right, there will be no output and you'll have a new file in the same folder called company_findings.csv
5b. If the script outputs anything, you'll need to udpate the "severities" or "cloud_mappings" dictionaries at the top of this script. 
    5b1. For Severities, add the insight name as the key, and the severity as an integer for the value. Severe = 4, Critical = 5
    5b2. For Clouds, add the account_id as the key, and "AWS, GCP, or Azure" as the value
6. Run the script again after that and repeat if necessary until there's no output. 
'''
# To do: 
# - Dynamically pull the clouds list from a Divvy instance
# - Dynamically pull all insight severities

import csv

severities = {
  'Instances Not in SBX  W/ Public IP': 4,
  'Firewall rules open internet ingress': 4,
  'Instance W/ Internet Gateway Exposing RDP-Public': 5,
  'Instance W/ Internet Gateway Exposing SSH & RDP-Public': 5,
  'Instance Exceeding Core 16': 4,
  'Network Resource Without Traffic Logging Configured - AWS': 5,
  'Instance W/ Internet Gateway Exposing SSH-Public': 5,
  'Cloud Account Without Global API Accounting Config': 5,
  'SSL Certificate Expired': 4,
  'Cloud Root Account API Access Key Present': 5,
  'Database Instance Without Recent Snapshot': 4,
  'Load Balancer Access Logging Disabled': 4,
  'Storage Container Exposing Access To World': 5,
  'Cloud User Account Without MFA': 4,
  'Cloud Account Password Policy Missing': 4,
  'Cloud Account Without Users': 4,
  'Instance With Failed/Degraded Availability': 4,
  'Cloud Account Without Root Account MFA Protection': 5,
  'Database Instance Publicly Accessible With Attached Exposed Security Group': 5,
  'Database Instance Not Encrypted': 4,
  'Encryption Key Expired or Expiring Soon': 4,
  'Load Balancer Without SSL Listener': 4,
  'Big Data Instance Encryption Not Enabled': 4,
  'Network Without Traffic Logging': 5,
  'Snapshot Publicly Available': 5,
  'API Key Unused For 90 Days': 4,
  'API Accounting Not Exporting': 4,
  'Big Data Retention Policy Less Than Seven Days': 4,
  'Volume Encryption Not Enabled': 4,
  'API Accounting Config Log Exposed': 5,
  'Cloud Account Password Policy Not CIS-compliant': 4,
  'Access List Default Allows Ingress/Egress (Security Group)': 4,
  'Big Data Instance Without A Recent Manual Snapshot': 4,
  'Instance Exposing SSH To World': 5,
  'Storage Container Not Enforcing Encryption At Rest': 4,
  'API Accounting Config Without Encryption': 4,
  'Instance Not In Private Network': 4,
  'Encryption Key Not Supporting Key Rotation': 4,
  'Access List Exposes Non-Web Ports to World (Security Group)': 4,
  'Cloud Account Password Policy Does Not Require Symbols': 4,
  'Cloud Account Password Policy Does Not Require Lowercase': 4,
  'Cloud Account Password Policy Does Not Require Uppercase': 4,
  'Instance Without Any Tags': 4,
  'Volume Encryption Not Enabled With PHI Tags': 5,
  'Access List Exposes SSH to World (Security Group)': 5,
  'Cloud User With Stale API Credentials': 4,
  'Cloud Account Password Policy Length Too Short': 4,
  'Cloud Account Password Policy Does Not Require Numbers': 4,
  'Access List Exposes Windows RDP to World (Security Group)': 5,
  'Cloud Account Password Policy Age Too Long': 4,
  'Instance Multi-Tenant': 4,
  'Snapshot With PHI Unencrypted': 5,
  'Instance With a Public IP Exposing SSH': 5,
  'Storage Container With PHI Open To World': 5,
  'Cloud User Inactive': 4,
  "Memcache Instance Doesn't Enforce Encryption at Rest": 4,
  'Memcache Instance Transit Encryption Disabled': 4,
  "Elasticsearch Instance Doesn't Enforce Encryption at Rest": 4,
  'Security Rules Exposing Public Access to Vulnerable Services': 4,
  'Workspace Without Root Volume Encryption': 4,
  'Distributed Table Encryption Disabled': 4,
  'Distributed Table Has Backups Disabled': 4,
  'Distributed Table Cluster Open to World': 5,
  'Security Center Standard Pricing Tier Not Selected': 4,
  'Security Center Automatic Provisioning Of Monitoring Agent Is Off': 4,
  'Security Center System Updates Recommendation Is Off': 4,
  'Security Center Security Configurations Recommendation Is Off': 4,
  'Security Center Endpoint Protection Recommendation Is Off': 4,
  'Security Center Disk Encryption Recommendation Is Off': 4,
  'Security Center Network Security Groups Recommendation Is Off': 4,
  'Security Center Web Application Firewall Recommendation Is Off': 4,
  'Security Center Next Generation Firewall Recommendation Is Off': 4,
  'Security Center Vulnerability Assessment Recommendation Is Off': 4,
  'Security Center Storage Encryption Recommendation Is Off': 4,
  'Security Center JIT Network Access Recommendation Is Off': 4,
  'Security Center Adaptive Application Controls Recommendation Is Off': 4,
  'Security Center SQL Auditing & Threat Detection Recommendation Is Off': 4,
  'Security Center SQL Encryption Recommendation Is Off': 4,
  'Security Center Security Contact Emails Are Not Set': 4,
  'Security Center Security Contact Phone Number Is Not Set': 4,
  'Security Center Send Me Emails About Alerts Is Off': 4,
  'Security Center Send Email Also To Subscription Owners Is Off': 4,
  'Storage Container Not Enforcing Transit Encryption': 4,
  'Storage Container Exposed To The Public': 5,
  'Instance Exposing RDP To World': 4,
  'Database Instance Publicly Accessible': 4,
  'Cloud Policy With Full Access': 4,
  'Google Service Account With Admin Privileges': 4,
  'Database Instance Allowing Root Login From Any Host': 4,
  'Network Peers Connected to Unknown Accounts': 4,
  'Resource With Cross Account Access to Unknown Account': 5,
  'Instance With a Public IP Exposing RDP': 5,
  'Machine Learning Instance With Direct Internet Access Enabled': 4,
  'Machine Learning Instance With Root Access Enabled': 4,
  'EKS Container Cluster With Public Access Enabled': 4,
  'EKS Container Cluster With Private Access Disabled': 4,
  'Cloud Topic Exposed To Public': 5,
  'Cost - Services Exceeding Cost Allowance': 4,
  'S3 Bucket Data Exposure (supersecretbucket123)': 5,
  'S3 open and unencrypted': 5,
  'Demo - Instances not in US regions': 4,
  'Demo - Critical Threat Findings': 5,
  'David - Instances Running with ports open and have been scanned': 5,
  'Unencrypted DB instances': 4,
  'DB not in the right places': 4
}

cloud_mappings = {
    '018633262502':	'AWS',
    '765756409785':	'AWS',
    '941341221998':	'AWS',
    '011613360141':	'AWS',
    '160317567231':	'AWS',
    'claim-cmpben-carepls-sbx-7870':	'GCP',
    '788d0172-c030-4746-b72a-150ffeb686a7':	'Azure',
    '0713795f-c20b-4ca1-8810-9e87a2adb61d':	'Azure',
    '0b8cdb5c-a8f9-4f32-b49f-ff055bdbd09c':	'Azure',
    'cloudteam-monitoring-npe-2ab0':	'GCP',
    'cloudteam-monitoring-prd-12ad':	'GCP',
    'd17c0d9c-1e34-4b5d-b55e-5eddb6e305bf':	'Azure',
    'cs-esb-wit-sbx-4372':	'GCP',
    'cs-ppcm-docrep-sbx-3861':	'GCP',
    'cs-sop-rsodp-sbx-c82b':	'GCP',
    'cs-war-ewal-sbx-1cd5':	'GCP',
    'cs-war-go365-sbx-17e7':	'GCP',
    'dc3d69d6-bb65-4765-8cd6-1d12a96a50a5':	'Azure',
    '9cb3ff2b-0dcd-43f7-a57d-5940d03ad89b':	'Azure',
    'dha-consumer-fblppoc-npe-1c19':	'GCP',
    'dha-consumer-monitor-npe-32c2':	'GCP',
    'dha-dec-care-coach-npe-6e83':	'GCP',
    'dha-dec-care-coach-prd-eaa5':	'GCP',
    'dha-dec-compass-npe-ab37':	'GCP',
    'dha-dec-compass-prd-6833':	'GCP',
    'dha-dec-mflow-npe-4443':	'GCP',
    'dha-dec-mflow-prd-c080':	'GCP',
    'dha-dec-mflow-trn-npe-e5fe':	'GCP',
    'dha-dec-mflow-trn-prd-2c62':	'GCP',
    'dha-dec-monitoring-npe-03a3':	'GCP',
    'dha-dec-monitoring-prd-e927':	'GCP',
    'dha-dec-movi-npe-1551':	'GCP',
    'dha-dec-movi-prd-1176':	'GCP',
    'dha-dec-poc-sbx-aeea':	'GCP',
    '8fa1a1cb-f416-46fa-9b27-adc1888b74c2':	'Azure',
    'ffceafa5-d6c9-43fe-8b58-461829cfce4e':	'Azure',
    'dha-eda-dplrnpoc-npe-6563':	'GCP',
    'dha-eda-monitoring-npe-f558':	'GCP',
    'dha-eda-syndatapoc-npe-8d2c':	'GCP',
    'a5debc07-f73f-4bf3-b121-a87b8aba4bb3':	'Azure',
    'fc0643d5-560e-4c25-b76d-b04ae491c8d2':	'Azure',
    'dse-cem-api-sbx-8dd2':	'GCP',
    'dse-cemob-da-npe-7153':	'GCP',
    'dse-cemob-da-prd-fa2d':	'GCP',
    'dse-cemob-go365mdcaid-npe-1931':	'GCP',
    'dse-cemob-go365mdcaid-prd-613f':	'GCP',
    'dse-cemob-monitoring-npe-48e5':	'GCP',
    'dse-cemob-monitoring-prd-027c':	'GCP',
    'dse-consvc-mentor-npe-640e':	'GCP',
    'dse-consvc-mentor-prd-9e32':	'GCP',
    'dse-consvc-monitoring-npe-17bc':	'GCP',
    'dse-consvc-monitoring-prd-08c8':	'GCP',
    'dse-vtpi-bpic-sbx-01c0':	'GCP',
    'dse-vtpi-ivrnuance-sbx-cef4':	'GCP',
    'dummy-project-sbx-e429':	'GCP',
    'ea-eias-techeval-sbx-4105':	'GCP',
    'a9e53f05-d7b0-41b3-bc4a-78dd25d283f0':	'Azure',
    'b73eea45-4219-411f-ab84-1b65a9784a76':	'Azure',
    'eip-cloud-rnd-sbx-9b11':	'GCP',
    '5bb82b06-f0cf-4618-84b0-c4d7f133a5ba':	'Azure',
    'e1a9f4e8-efb8-480a-90fc-1ce5548bd749':	'Azure',
    'b96718ce-e030-448b-b0a3-471af3a8a3b7':	'Azure',
    '0bcf5a0a-8edc-40b4-a36d-d78fc5be0a5b':	'Azure',
    'hcs-ecom-ccext-npe-d040':	'GCP',
    'hcs-ecom-ccext-prd-92dc':	'GCP',
    'hcs-ecom-ecom-sbx-b19c':	'GCP',
    'hcs-ecom-monitoring-npe-baa8':	'GCP',
    'hcs-ecom-monitoring-prd-7049':	'GCP',
    'hcs-ecom-odos-npe-4584':	'GCP',
    'hcs-ecom-odos-prd-271c':	'GCP',
    'hcs-hah-odosdev-sbx-203e':	'GCP',
    'hcs-mr-hrie-sbx-04fe':	'GCP',
    'hcs-mr-hrsn-sbx-f335':	'GCP',
    'hcs-pbm-monitoring-npe-2b3b':	'GCP',
    'hcs-pbm-monitoring-prd-06e9':	'GCP',
    'hcs-pbm-oml-npe-e223':	'GCP',
    'hcs-pbm-oml-prd-0164':	'GCP',
    'hcs-pbm-rxcl-sbx-4529':	'GCP',
    'hcs-pbm-rxclwdi-npe-0c49':	'GCP',
    'hcs-pbm-rxclwdi-prd-b639':	'GCP',
    'hcs-pbm-rxconnectpoc-npe-59fe':	'GCP',
    'hcs-pbm-rxconsult-sbx-38d4':	'GCP',
    'hcs-pbm-rxgladiators-sbx-1724':	'GCP',
    'hcs-pbm-rxoml-sbx-4ef2':	'GCP',
    'hcs-pbm-rxop-sbx-c844':	'GCP',
    'hcs-pbm-rxopappeal-npe-ab16':	'GCP',
    'hcs-pbm-rxopappeal-prd-597b':	'GCP',
    'hcs-pbm-silentheroes-sbx-8af5':	'GCP',
    'hcs-pbm-werx-sbx-aa58':	'GCP',
    'hcs-phffmt-apis-npe-30b0':	'GCP',
    'hcs-phffmt-apis-prd-7b32':	'GCP',
    'hcs-phffmt-devteam-sbx-af5d':	'GCP',
    'hcs-phffmt-monitoring-npe-3c27':	'GCP',
    'hcs-phffmt-monitoring-prd-57f1':	'GCP',
    'hcs-prov-monitoring-npe-8961':	'GCP',
    'hcs-prov-monitoring-prd-be24':	'GCP',
    'hcs-prov-pmdm-npe-2fc8':	'GCP',
    'hcs-prov-pmdm-prd-2859':	'GCP',
    'hcs-rxpbm-rxconnect-sbx-7320':	'GCP',
    '169380453451':	'AWS',
    'hpe-hpse-cd-sbx-a6f0':	'GCP',
    'hum-dha-com-npe-1b68':	'GCP',
    'hum-dha-com-prod-d789':	'GCP',
    'hum-dha-eda-rds-sbx-228721':	'GCP',
    'hum-dha-gke-npe-1b68':	'GCP',
    'hum-dha-gke-prod-d789':	'GCP',
    'hum-dha-net-npe-1b68':	'GCP',
    'hum-dha-net-prod-d789':	'GCP',
    'hum-dha-paas-poc-sbx':	'GCP',
    'hum-dplrnpoc-net-temp-7817':	'GCP',
    'hum-dse-com-npe-8bfd':	'GCP',
    'hum-dse-com-prod-457b':	'GCP',
    'hum-dse-gke-npe-8bfd':	'GCP',
    'hum-dse-gke-prod-457b':	'GCP',
    'hum-dse-net-npe-8bfd':	'GCP',
    'hum-dse-net-prod-457b':	'GCP',
    'hum-fblppoc-net-temp-5438':	'GCP',
    'hum-global-com-npe-6663':	'GCP',
    'hum-global-com-prod-d993':	'GCP',
    'hum-global-mon-npe-6663':	'GCP',
    'hum-global-mon-prod-d993':	'GCP',
    'hum-global-net-npe-6663':	'GCP',
    'hum-global-net-prod-d993':	'GCP',
    'hum-global-sec-npe-6663':	'GCP',
    'hum-global-sec-prod-d993':	'GCP',
    'hum-hcs-com-npe-b6f5':	'GCP',
    'hum-hcs-com-prod-0430':	'GCP',
    'hum-hcs-gke-npe-b6f5':	'GCP',
    'hum-hcs-gke-prod-0430':	'GCP',
    'hum-hcs-net-npe-b6f5':	'GCP',
    'hum-hcs-net-prod-0430':	'GCP',
    'hum-hcs-rapid-fhir-sbx':	'GCP',
    'hum-humshared-ea-eca-sbx':	'GCP',
    'hum-humsrd-com-npe-1666':	'GCP',
    'hum-humsrd-com-prod-00b1':	'GCP',
    'hum-humsrd-gke-npe-1666':	'GCP',
    'hum-humsrd-gke-prod-00b1':	'GCP',
    'hum-humsrd-net-npe-1666':	'GCP',
    'hum-humsrd-net-prod-00b1':	'GCP',
    'hum-ima-aae-adminteam-sbx':	'GCP',
    'hum-ima-com-npe-995f':	'GCP',
    'hum-ima-com-prod-5596':	'GCP',
    'hum-ima-dataplatfrm-comcor-sbx':	'GCP',
    'hum-ima-gke-npe-995f':	'GCP',
    'hum-ima-gke-prod-5596':	'GCP',
    'hum-ima-net-npe-995f':	'GCP',
    'hum-ima-net-prod-5596':	'GCP',
    'hum-master-terraform-sbx':	'GCP',
    'hum-shared-iti-cldplatform-sbx':	'GCP',
    'hum-syndatapoc-net-temp-1278':	'GCP',
    'hum-global-sec-npe-6663':	'GCP',
    '443427132666':	'AWS',
    '311848308606':	'AWS',
    '672082021463':	'AWS',
    '357596259309':	'AWS',
    '797107702067':	'AWS',
    '523099395929':	'AWS',
    '200391145030':	'AWS',
    '246517805225':	'AWS',
    '631160628897':	'AWS',
    '363531624048':	'AWS',
    '312105934461':	'AWS',
    '333189847664':	'AWS',
    '531631487654':	'AWS',
    '489484484341':	'AWS',
    '972774723820':	'AWS',
    '811536652220':	'AWS',
    '099692903901':	'AWS',
    '975039649047':	'AWS',
    '844338057902':	'AWS',
    '546393961047':	'AWS',
    '325633442068':	'AWS',
    'humsrd-cloud-testmod-npe-1456':	'GCP',
    'humsrd-cloud-testmod-prd-0d1c':	'GCP',
    'humsrd-cloud-testprj-npe-3904':	'GCP',
    'humsrd-cloud-testprj-prd-126e':	'GCP',
    'humsrd-dbs-dba-npe-ded8':	'GCP',
    'humsrd-dbs-dba-prd-63a1':	'GCP',
    'humsrd-dbs-dba-sbx-0eaf':	'GCP',
    'humsrd-dbs-monitoring-npe-ade8':	'GCP',
    'humsrd-dbs-monitoring-prd-2ed7':	'GCP',
    'humsrd-ea-eca-npe-4696':	'GCP',
    'humsrd-ea-eca-prd-cbe9':	'GCP',
    'humsrd-ea-etm-apic-sbx-a180':	'GCP',
    'humsrd-ea-monitoring-npe-f28e':	'GCP',
    'humsrd-ea-monitoring-prd-1e97':	'GCP',
    'humsrd-hpse-itea-npe-c0ad':	'GCP',
    'humsrd-hpse-itea-prd-443e':	'GCP',
    'humsrd-hpse-itea-sbx-b980':	'GCP',
    'humsrd-hpse-monitor-npe-d384':	'GCP',
    'humsrd-hpse-monitor-prd-4a4b':	'GCP',
    'humsrd-iti-lrgsys-sbx-433a':	'GCP',
    'humsrd-ops-vault-poc-sbx':	'GCP',
    'humsrd-stackdriver-sbx-f7a5':	'GCP',
    '511293253270':	'AWS',
    'ima-aae-dv-npe-b8a2':	'GCP',
    'ima-aae-dv-prd-4eff':	'GCP',
    'ima-aae-efl-npe-2556':	'GCP',
    'ima-aae-efl-prd-cdb0':	'GCP',
    'ima-aae-monitoring-npe-68dc':	'GCP',
    'ima-aae-monitoring-prd-81aa':	'GCP',
    'ima-aae-nzpoc-npe-d272':	'GCP',
    'ima-edts-cdf-npe':	'GCP',
    'ima-edts-cdf-prd':	'GCP',
    'ima-edts-comcor-npe-263c':	'GCP',
    'ima-edts-comcor-prd-833b':	'GCP',
    'ima-edts-hep-npe-06e9':	'GCP',
    'ima-edts-hep-prd-3061':	'GCP',
    'ima-edts-monitoring-npe-0bf7':	'GCP',
    'ima-edts-monitoring-prd-eca0':	'GCP',
    'ima-edts-ose2intern-sbx-044c':	'GCP',
    'ima-edw-netfin-sbx-58f3':	'GCP',
    'ima-hqpa-monitoring-npe-1a5b':	'GCP',
    'ima-hqpa-monitoring-prd-df2b':	'GCP',
    'ima-hqpa-stars-sbx-b9c2':	'GCP',
    'ima-hqpa-starstv-npe-466b':	'GCP',
    'ima-hqpa-starstv-prd-abe9':	'GCP',
    'c4f076b0-d3d9-4f58-b565-6c303e76c8e7':	'Azure',
    '2df1340b-45e7-4f28-a65e-dc2ecefec587':	'Azure',
    '69f17c09-86d0-4fb4-81a8-8952f51d49c2':	'Azure',
    'b7a058d3-16af-412c-a076-3bb66a1b5439':	'Azure',
    'itta-pdx-blkchn-sbx-294b':	'GCP',
    '974948f0-2b2e-45bb-be87-98effcfdbf61':	'Azure',
    'ab6374bc-7d5d-4cfb-b224-9f4560bfe22d':	'Azure',
    'dd6b8ad6-ee16-451f-99cc-ead55a2976ab':	'Azure',
    '02dfd7e5-ab3b-4748-8744-41a4163e545a':	'Azure',
    'provider-sgh1-pmdm-sbx-e992':	'GCP',
    '28820cfb-8dad-4204-b79d-3d1257a758cf':	'Azure',
    'f199de56-a6ef-427c-82b3-3af83544c41d':	'Azure',
    '343ee394-ba45-424a-8c80-eb113154cff8':	'Azure',
    'e196e375-ae65-4518-9165-6330faf97e9a':	'Azure',
    '773b59e3-082f-46b7-8552-4c82d0e82bc4':	'Azure',
    '1e72e1c4-abe8-4680-9a2c-2d4526592bd6':	'Azure',
    'sre-tower11-pbmmon-sbx-70f1':	'GCP',
    'sre-tower12-psmapi-sbx-288c':	'GCP',
    'sre-unit1-twr7-sbx-c8c2':	'GCP',
    'terraform-bootstrap-220514':	'GCP',
    '042805010333':	'AWS',
    '068955290847':	'AWS',
    '048503856623':	'AWS',
    '011460987434':	'AWS',
    'f1b7d44e-77b7-4a61-8d98-b5ad702661b4':	'Azure',
    'f4802121-0e30-40ce-b60d-e0d566b678a1':	'Azure'
}

unknown_insight_severities = []
unknown_clouds = []

with open('company_csv_unformatted.csv', 'r') as f:
    reader = csv.reader(f)
    csv_list = list(reader)

    with open('company_findings.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        
        header = csv_list.pop(0)
        header.append('Severity')
        header.append('Cloud')
        writer.writerow(header)
          
        for insight_row in csv_list:
            if "\n" in insight_row[6]:
                insight_violations = insight_row[6].splitlines()
                
                for insight in insight_violations:
                    temp_insight_row = insight_row[0:6]
                    temp_insight_row.append(insight)
                    try:
                        temp_insight_row.append(severities[insight])
                    except KeyError as e:
                        unknown_insight_severities.append(insight)

                    try:
                        cloud_id = insight_row[1]
                        temp_insight_row.append(cloud_mappings[cloud_id])
                    except KeyError as e:
                        unknown_clouds.append(cloud_id)

                    writer.writerow(temp_insight_row) 

            else:
                try:
                    insight = insight_row[6]
                    insight_row.append(severities[insight])
                except KeyError as e:
                    unknown_insight_severities.append(insight)

                try:
                    cloud_id = insight_row[1]
                    insight_row.append(cloud_mappings[cloud_id])
                except KeyError as e:
                    unknown_clouds.append(cloud_id)        

                writer.writerow(insight_row)                


severities_to_look_up = set(unknown_insight_severities)
clouds_to_look_up = set(unknown_clouds)

if len(severities_to_look_up) > 0:
    print("List of insight severities to look up and add to the list: " + str(severities_to_look_up))

if len(clouds_to_look_up) > 0:
    print("List of cloud IDs to look up and add to the cloud types list: " + str(clouds_to_look_up))    

