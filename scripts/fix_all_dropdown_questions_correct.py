"""
HOTSPOT 드롭다운 문제들을 PDF에서 제대로 추출해서 수정
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 각 문제별 올바른 내용 (PDF에서 수동 확인)
QUESTION_DATA = {
    104: {
        "question": "You can move a VM and its associated resources to a different subscription by using the Azure portal _______",
        "options": [
            "Yes",
            "No"
        ],
        "answer": "A"
    },
    115: {
        "question": "Data that is stored in the Archive access tier of an Azure Storage account _______",
        "options": [
            "can be accessed at any time by using azcopy.exe",
            "can only be read by using Azure Backup",
            "must be restored before the data can be accessed",
            "must be rehydrated before the data can be accessed"
        ],
        "answer": "D"
    },
    118: {
        "question": "An Availability Zone in Azure has physically separate locations _______",
        "options": [
            "across two continents",
            "within a single Azure region",
            "within multiple Azure regions",
            "within a single Azure datacenter"
        ],
        "answer": "B"
    },
    132: {
        "question": "You plan to deploy 20 virtual machines to an Azure environment. To ensure that a virtual machine named VM1 cannot connect to the other virtual machines, VM1 must _______",
        "options": [
            "be deployed to a separate virtual network",
            "run a different operating system than the other virtual machines",
            "be deployed to a separate resource group",
            "have two network interfaces"
        ],
        "answer": "A"
    },
    188: {
        "question": "You can access Compliance Manager from the _______",
        "options": [
            "Azure Active Directory admin center",
            "Azure portal",
            "Microsoft 365 admin center",
            "Microsoft Service Trust Portal"
        ],
        "answer": "D"
    },
    212: {
        "question": "Azure Databricks is an Apache Spark-based analytics platform. The platform consists of several components including Machine Learning library. You want to use Databricks machine learning library to _______",
        "options": [
            "train a machine learning model",
            "implement linear algebra",
            "implement computer vision",
            "run SQL queries"
        ],
        "answer": "A"
    },
    219: {
        "question": "You can use Azure Activity Log to view which user turned off a specific virtual machine during the last 14 days _______",
        "options": [
            "Yes",
            "No"
        ],
        "answer": "A"
    },
    251: {
        "question": "You can enable just-in-time (JIT) VM access by using _______",
        "options": [
            "Azure Bastion",
            "Azure Firewall",
            "Azure Front Door",
            "Azure Security Center"
        ],
        "answer": "D"
    },
    265: {
        "question": "You can view your company's regulatory compliance report from _______",
        "options": [
            "Azure Advisor",
            "Azure Analysis Services",
            "Azure Monitor",
            "Azure Security Center"
        ],
        "answer": "D"
    },
    281: {
        "question": "An Azure service is available to all Azure customers when it is in _______",
        "options": [
            "public preview",
            "private preview",
            "development",
            "an Enterprise Agreement (EA) subscription"
        ],
        "answer": "A"
    },
    296: {
        "question": "The Microsoft Privacy Statement explains what personal data Microsoft processes, how Microsoft processes the data, and _______",
        "options": [
            "the purposes for processing the data",
            "how to contact Microsoft",
            "how to request deletion of the data",
            "the retention period for the data"
        ],
        "answer": "A"
    },
    297: {
        "question": "Authentication is the process of verifying a user's _______",
        "options": [
            "credentials",
            "authorization",
            "access level",
            "role"
        ],
        "answer": "A"
    },
    306: {
        "question": "You can configure a lock on a resource group to prevent the accidental deletion of the resource group _______",
        "options": [
            "Yes",
            "No"
        ],
        "answer": "A"
    },
    310: {
        "question": "An Azure service is available to all Azure customers when it is in _______",
        "options": [
            "public preview",
            "private preview",
            "development",
            "an Enterprise Agreement (EA) subscription"
        ],
        "answer": "A"
    },
    329: {
        "question": "Budget alerts notify you when spending, based on usage or cost, reaches or exceeds the amount defined in the alert condition of the budget _______",
        "options": [
            "Yes",
            "No"
        ],
        "answer": "A"
    },
    338: {
        "question": "If the SLA for an Azure service is not met, you receive a credit that can be applied to your bill _______",
        "options": [
            "Yes",
            "No"
        ],
        "answer": "A"
    },
    372: {
        "question": "All Azure services that are in public preview are _______",
        "options": [
            "provided without any documentation",
            "only configurable from Azure CLI",
            "excluded from the Service Level Agreements",
            "only configurable from the Azure portal"
        ],
        "answer": "C"
    }
}

def update_all_questions():
    """모든 문제 업데이트"""
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = []
    
    for q_id, q_data in QUESTION_DATA.items():
        print(f"\nQ{q_id} 업데이트 중...")
        print(f"  문제: {q_data['question'][:80]}...")
        
        # JSON에서 해당 문제 찾아서 수정
        for q in data['questions']:
            if q['id'] == q_id:
                q['question'] = q_data['question']
                q['questionType'] = 'MULTIPLE_CHOICE'
                
                # 선택지 생성
                options = []
                for i, opt_text in enumerate(q_data['options']):
                    options.append({
                        'letter': chr(65 + i),
                        'text': opt_text
                    })
                
                q['options'] = options
                q['answer'] = q_data['answer']
                
                # dropdowns 제거
                if 'dropdowns' in q:
                    del q['dropdowns']
                
                updated.append(q_id)
                print(f"  ✓ 업데이트 완료")
                break
    
    # 저장
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"✓ 업데이트 완료: {len(updated)}개")
    print(f"   {sorted(updated)}")
    print(f"\n{'='*60}")

if __name__ == "__main__":
    update_all_questions()

