> 📖 Read this in [中文](./README_zh-CN.md)
# Introduction to standard datasets


Here are four standard datasets, namely the standard case dataset, the standard event dataset, the standard event classification dataset, and the manually labeled risk-related case dataset


## Standard case dataset
standard_cases jsonl
The standard dataset obtained from the AIID and AIAAIC datasets, each of which is a case, and the attributes of the case include: case id, case title, case description, case body, etc


## Standard event dataset
standard_incidents jsonl
The time standard dataset obtained by aligning the standard case dataset through the event alignment project code, each of which is an event, and the properties of the event include: event id, list of case IDs corresponding to the event


## Standard event classification dataset
standard_incidents_classification json
According to the MIT and AI risk classification standards and the European Union AI risk classification standards, each event in the standard event dataset is manually classified into risk categories. Each of these items is the classification result of an event. The attributes of the classification results include: event id, entity classification result, intent classification result, time classification result, European Union risk classification result and the domain classification result. The domain classification result is a classification list with multiple classification results, that is, event A can belong to both domain 1 and domain 2, which we think is more in line with the actual situation. Each element in the list includes a domain classification and sub-domain classification.


## Manual labeling of risk-related case datasets
standard_incidents_human_label_classification json
A dataset used to test the indicators of the llm filtering method in the step of "AI-related news to AI-risk-related news". 2000 AI-related news were randomly selected from the official AI-related case dataset, manually labeled whether it was related to AI risk, and the results were compared with the llm filtering results to evaluate the index performance of the llm filtering method.


# Datasets during processing


## AIAAIC
AIAAIC_Repository and aiaaic_processed_data jsonl
AIAAIC_Repository is a dataset downloaded from the AIAAIC website, aiaaic_processed_data is a dataset obtained by extracting case elements from a large model


## AIID
AIID_reports is a dataset downloaded from the AIID website AIID_incident jsonl is a dataset obtained after processing




# AI Risk Classification Framework
Note that due to translation issues, the framework may not be exactly the same as the original text. For an accurate classification of the framework, please refer to the MIT Classification Framework and the original text of the European Union artificial intelligence security act.
## The causal classification framework

### Entity classification

| ID | Category | Level | Description |
|----|----------|-------|-------------|
| 0  | Entity   | Artificial Intelligence | Risks arise from decisions or actions made by artificial intelligence systems |
| 1  | Entity   | Human                   | Risk is caused by human decisions or actions |
| 2  | Entity   | Other                   | Risks are caused by other reasons or are unclear |

### Intent classification

| ID | Category | Level       | Description |
|----|----------|-------------|-------------|
| 0  | Intent   | Intentional | Risk arises from the expected outcome of pursuing goals |
| 1  | Intent   | Unintentional | Risk results from unexpected outcomes in pursuit of goals |
| 2  | Intent   | Other         | Risks are described as occurring, but their intent is not clearly stated |

### Time classification

| ID | Category | Level          | Description |
|----|----------|----------------|-------------|
| 0  | Time     | Pre-deployment | Risks exist before artificial intelligence deployment |
| 1  | Time     | Post-deployment | Risk occurs after artificial intelligence model training and deployment |
| 2  | Time     | Other          | Risk does not specify time of occurrence |


---

## Domain Classification Framework

### Level 1 field classification
| Domain ID | Domain Name | Description | ID |
|--------| ------------------------------- | ---------------------------------------------------------------------- |-----|
| 1 | Discrimination and toxicity | Unequal treatment of individuals or groups by artificial intelligence | 1 |
| 2 | Privacy and Security | Risks Involving Data Privacy and System Security | 2 |
| 3 | Misinformation | Risks arising from false or misleading information | 3 |
| 4 | Malicious actors | Using AI for large-scale misinformation or attacks | 4 |
| 5 | Human-machine interaction | Overdependence or loss of autonomy in human-AI interaction | 5 |
| 6 | Socioe****mic and Environmental | The Impact of AI on Socioe****mic Structure and the Environment | 6 |
| 7 | Security, failures, and limitations of artificial intelligence systems | AI systems' own security bugs, capability deficiencies, or ethical conflicts | 7 |

### Secondary subdomain classification
| Domain ID | Subdomain ID | Subdomain Name | Description | ID |
|--------|--------| ------------------------ | ---------------------------------------------------------------------- |-----|
| 1 | 1.1 | Unfair discrimination and misrepresentation | Artificial intelligence's unequal treatment of individuals or groups, often based on race, gender, or other sensitive characteristics, results in unfair outcomes and representation of those groups. | 8 |
| 1 | 1.2 | Exposure to Toxic Substances | AI presents users with harmful, abusive, unsafe, or inappropriate content. May involve AI creating, describing, advising, or encouraging action. Examples of harmful content include hate speech, violence, extremism, illegal behavior, child sexual abuse material, and content that violates community norms, such as profanity, inflammatory political speech, or pornography. | 9 |
| 1 | 1.3 | The performance of each group was uneven |The accuracy and effectiveness of artificial intelligence decisions and actions depend on group membership, and decisions in artificial intelligence system design and biased training data can lead to unequal outcomes, reduced benefits, increased workload, and user alienation.| 10 |
| 2 | 2.1 | Obtaining, leaking, or correctly inferring sensitive information, violating privacy | Artificial intelligence systems can remember and disclose sensitive personal data or infer personal privacy information without the individual's consent. Accidental or unauthorized sharing of data and information may compromise users' privacy expectations, facilitate identity theft, or lose confidential intellectual property. | 11 |
| 2 | 2.2 | artificial intelligence system security bugs and attacks | Vulnerabilities that may be exploited in artificial intelligence systems, software power builders, and hardware, resulting in unauthorized access, data and privacy leakage, or system manipulation, resulting in insecure output or behavior. | 12 |
| 3 | 3.1 | False or misleading information | Artificial intelligence systems inadvertently generate or disseminate incorrect or deceptive information, which may cause users to develop false beliefs and undermine their autonomy. Humans who make decisions based on false beliefs may suffer physical, emotional or material harm | 13 |
| 3 | 3.2 | Info-ecological pollution and lack of consensus | Highly personalized artificial intelligence-generated misinformation creates "filter bubbles" in which individuals see only content that fits their existing beliefs, undermining shared realities and weakening social cohesion and political processes. | 14 |
| 4 | 4.1 | Mass misinformation, surveillance, and influence | The use of artificial intelligence systems for mass disinformation, malicious surveillance, or targeted sophisticated automated censorship and propaganda with the aim of manipulating the political process, public opinion, and behavior. | 15 |
| 4 | 4.2 | Cyber Attacks, Weapon Development or Use, and Mass Harm | Use artificial intelligence systems to develop cyber weapons (e.g., write cheaper and more effective malicious software), develop new weapons or enhance existing weapons (e.g., Lethal Autonomous Weapons or CBRNE), or use weapons to cause mass harm. | 16 |
| 4 | 4.3 | Fraud, Scams, and Targeted Manipulation | Use artificial intelligence systems for personal advantage, such as through deception, scams, scams, extortion, or targeted manipulation of beliefs or behavior. For example, use artificial intelligence for research or education to plagiarize, impersonate a trusted or false individual for improper financial gain, or produce humiliating or pornographic images. | 17 |
| 5 | 5.1 | Over-reliance and unsafe use | Users personify, trust, or rely on artificial intelligence systems, resulting in emotional or material dependence on artificial intelligence systems, as well as inappropriate relationships or expectations with artificial intelligence systems. Trust can be exploited by malicious actors (e.g., theft of personal information or manipulation), or the improper use of artificial intelligence in critical situations (e.g., medical emergencies) can cause harm. Over-reliance on artificial intelligence systems can compromise autonomy and weaken social bonds. | 18 |
| 5 | 5.2 | Loss of human agency and autonomy | Humans delegating critical decisions to artificial intelligence systems, or artificial intelligence systems making decisions that reduce human control and autonomy, may cause humans to feel powerless, lose their ability to shape fulfilling life trajectories or become cognitively impaired. | 19 |
| 6 | 6.1 | Concentration of power and unfair distribution of benefits | Artificial intelligence results in the concentration of power and resources in certain entities or groups, especially those that can use or have powerful artificial intelligence systems, resulting in uneven distribution of benefits and exacerbation of social inequality. | 20 |
| 6 | 6.2 | Rising inequality, declining quality of jobs | Widely used artificial intelligence plus | 21 |
| 6 | 6.3 | Economic and cultural devaluation of human effort | Artificial intelligence systems capable of creating economic or cultural value, including by replicating human innovation or creativity (e.g., art, music, writing, code, inventions), may disrupt economic and social systems that depend on human effort. This may lead to a reduced appreciation of human skills, disruption of creative and knowledge-based industries, and homogenization of cultural experiences due to the pervasiveness of artificial intelligence-generated content. | 22 |
| 6 | 6.4 | Competitive landscape | Artificial intelligence developers or state-like actors engage in the artificial intelligence "race" by rapidly developing, deploying, and applying artificial intelligence systems to maximize strategic or economic advantage, which increases the risk of them releasing insecure and error-prone systems. | 23 |
| 6 | 6.5 | Governance Failure | Regulatory frameworks and oversight mechanisms are inadequate and fail to keep pace with the development of artificial intelligence, resulting in weak governance and an inability to properly manage artificial intelligence risks. | 24 |
| 6 | 6.6 | Environmental Hazards | The development and operation of artificial intelligence systems can cause environmental hazards, such as energy consumption in data centers, or materials and carbon footprints associated with artificial intelligence hardware. | 25 |
| 7 | 7.1 | Artificial intelligence pursuing its own goals conflicts with human goals or values | The behavior of artificial intelligence systems conflicts with human goals or values, especially those of designers or users, or ethical standards. These inconsistent behaviors may be introduced by humans during the design and development process, such as by rewarding hackers and target misgeneralizations, or may be the result of artificial intelligence using dangerous capabilities (e.g. manipulation, deception, situational awareness) to seek power, self-proliferate, or achieve other goals. | 26 |
| 7 | 7.2 | Artificial intelligence has dangerous capabilities | Artificial intelligence systems develop, access, or acquire capabilities that increase the potential to cause mass harm through deception, weapons development and acquisition, persuasion and manipulation, political strategy, cyberattacks, artificial intelligence development, situational awareness, and self-proliferation. These capabilities may cause mass harm due to malicious human actors, dysfunctional artificial intelligence systems, or malfunctions of artificial intelligence systems. | 27 |
| 7 | 7.3 | Lack of capability or robustness | Artificial intelligence systems cannot operate reliably or efficiently under different conditions, leading to errors and failures with serious consequences, especially in critical applications or areas requiring ethical reasoning. | 28 |
| 7 | 7.4 | Lack of transparency or interpretability | Challenges in understanding or interpreting the decision-making process of artificial intelligence systems, which can lead to mistrust, difficulty in enforcing compliance standards or holding relevant actors accountable for harms, and inability to identify and correct errors. | 29 |
| 7 | 7.5 | artificial intelligence benefits and rights | Ethical considerations regarding the treatment of potentially sentient artificial intelligence entities, including a discussion of their potential rights and benefits, particularly as artificial intelligence systems become more advanced and autonomous. | 30 |


## European Union artificial intelligence Act (AI Act) risk classification and regulatory rules

### 0.Unacceptable Risk

#### Definition and Scope
AI systems that pose a serious and irreversible threat to human security, fundamental rights, or democratic values will be banned from development, deployment, and use.

#### Specific prohibited scenarios
- ** Social scoring system **
Government or private institutions rate individuals based on their behavior, social relationships, and other attributes, leading to systemic discrimination or denial of rights.
Exception: Non-automated human social assessments (e.g., human credit scoring) are excluded.
- ** Real-time remote biometric monitoring **
Real-time facial recognition in public places (e.g. streets, shopping malls), unless used in strictly limited scenarios such as counter-terrorism and searching for felony suspects.
Non-real-time or non-remote biometrics (e.g. phone unlocking) are not subject to this restriction.
- ** subconscious manipulation technique **
Exploiting human weaknesses (e.g. cognitive deficits in children) to induce risky behaviors (e.g. AI toys that encourage self-harm).
- Significantly impair users' autonomous decision-making ability through covert interface design or psychological cues.

---

### 1.High Risk
#### Definition and determination criteria
AI systems are classified as high risk if they are likely to have a significant impact on health, safety, fundamental rights, or the environment in the following areas:
1. Critical infrastructure (e.g. power grids, traffic signal AI control systems)
2. ** Education and Vocational Training ** (Automated Test Scoring, Admission/Recruitment Screening)
3. ** Employment and labor management ** (resume screening algorithm, performance review system)
4. ** Public services and benefits ** (credit scoring, social security eligibility determination)
5. Law Enforcement and Justice (Predictive Policing, Electronic Surveillance, Evidence Reliability Assessment)
6. ** Immigration and Border Control ** (visa threat and risk assessment, biometric border checks)
7. ** Medical and Health ** (AI-assisted diagnostic equipment, surgical robots)

#### compliance requirements detailed
##### threat and risk assessment and mitigation
A ** prior impact assessment ** must be conducted, including:
Data bias analysis (e.g. risk of race, gender discrimination)
Simulation of the potential consequences of system failure (e.g. medical AI misdiagnosis scenarios)
User Rights Impact Report (Privacy, Right to Know, etc.)

##### Data governance
The training dataset must meet the following requirements:
- ** Representation **: Covering diverse groups of people to avoid discrimination
Traceability: recording data sources and labeling methods
- ** Security **: Compliant with privacy protection standards such as GDPR

##### technical documents and transparency
Provide detailed technical documents (at least):
System architecture and decision logic description
- threat and risk assessment results and mitigation measures
Test protocols and performance metrics (e.g. accuracy, fairness metrics)
- The user interface needs to clearly prompt AI to participate in decision-making (e.g. "This recruitment result was generated by the AI system")

##### Third Party Audit
High-risk systems are subject to conformity assessment by a designated body of the European Union, including:
Code audit (verifying compliance with claimed functionality)
Data quality review (to detect bias and mislabeling)
- Actual scenario stress testing

---

### 2.Limited Risk
#### Definition and characteristics
AI systems that have a foreseeable but not serious impact on user rights need to be managed through transparency.

#### Concrete types and rules
Generative AI (e.g. ChatGPT)
- ** content labeling obligations **:
All AI-generated content (text, images, videos) must be tagged with a non-removable identifier (e.g. "This content was generated by AI").
- Deepfakes must be annotated with the source of the original material (e.g. "based on XX actor image synthesis").

Emotion Recognition and Biometric Classification
- ** Dual consent mechanism **:
- User affirmative consent is required before first use (e.g. "This system will analyze your facial expressions").
- Provides real-time off options (e.g. disabling sentiment analysis in video conferencing).

##### User rights protection
- ** Right to refuse **: Users can request human alternatives to AI decisions (such as customer service conversations being transferred to real people).
- ** Right to Explanation **: Users are entitled to a brief explanation of the AI decision (e.g. "Recommend this product because you have viewed congeneric products").

---

### 3.Low/Minimal Risk
#### Scope of application
AI applications that pose little threat to individuals or society encourage industry self-discipline.

#### Typical case
- ** Daily tools **:
- email spam filters (like Gmail Smart Categories)
Automatic typesetting tools (e.g. Grammarly syntax checker)
- ** Entertainment and Consumer **:
Game NPC behavioral AI (e.g. Cyberpunk 2077 character interaction)
- Non-targeted advertising recommendations (e.g. clothing recommendations based on the weather)