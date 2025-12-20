"""
Matching 문제 정확하게 수정 (PDF 기반)
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# PDF에서 확인한 정확한 내용
CORRECT_MATCHING = {
    82: {
        'question': 'You plan to use Azure to host two apps named App1 and App2. The apps must meet the following requirements:\n\n→ You must be able to modify the code of App1.\n→ Administrative effort to manage the operating system of App1 must be minimized.\n→ App2 must run interactively with the operating system of the server.\n\nWhich type of cloud service should you use for each app? To answer, select the appropriate options in the answer area.\n\nNOTE: Each correct selection is worth one point.',
        'items': [
            {
                'item': 'App1',
                'options': ['Infrastructure as a Service (IaaS)', 'Platform as a Service (PaaS)', 'Software as a Service (SaaS)'],
                'answer': 'Platform as a Service (PaaS)'
            },
            {
                'item': 'App2',
                'options': ['Infrastructure as a Service (IaaS)', 'Platform as a Service (PaaS)', 'Software as a Service (SaaS)'],
                'answer': 'Infrastructure as a Service (IaaS)'
            }
        ]
    },
    187: {
        'question': 'You have three virtual machines (VMs) that are included in an availability set.\n\nYou try to resize one of the VMs, but you get an error message saying the desired size is not available in the availability set.\n\nYou need to ensure that you can resize the VM.\n\nWhich tool or tools should you use on each computer? To answer, select the appropriate options.\n\nNOTE: Each correct selection is worth one point.',
        'items': [
            {
                'item': 'Computer1',
                'options': [
                    'The Azure CLI and the Azure portal',
                    'The Azure portal and Azure PowerShell',
                    'The Azure CLI and Azure PowerShell',
                    'The Azure CLI, the Azure portal, and Azure PowerShell'
                ],
                'answer': 'The Azure CLI and Azure PowerShell'
            },
            {
                'item': 'Computer2',
                'options': [
                    'The Azure CLI and the Azure portal',
                    'The Azure portal and Azure PowerShell',
                    'The Azure CLI and Azure PowerShell',
                    'The Azure CLI, the Azure portal, and Azure PowerShell'
                ],
                'answer': 'The Azure CLI and Azure PowerShell'
            },
            {
                'item': 'Computer3',
                'options': [
                    'The Azure CLI and the Azure portal',
                    'The Azure portal and Azure PowerShell',
                    'The Azure CLI and Azure PowerShell',
                    'The Azure CLI, the Azure portal, and Azure PowerShell'
                ],
                'answer': 'The Azure CLI, the Azure portal, and Azure PowerShell'
            }
        ]
    },
    249: {
        'question': 'You need to configure security features for your Azure subscription.\n\nWhich Azure service should you use? To answer, select the appropriate options.\n\nNOTE: Each correct selection is worth one point.',
        'items': [
            {
                'item': 'Monitor threats by using sensors',
                'options': [
                    'Azure Monitor',
                    'Azure Security Center',
                    'Azure Active Directory (Azure AD) Identity Protection',
                    'Azure Advanced Threat Protection (ATP)'
                ],
                'answer': 'Azure Advanced Threat Protection (ATP)'
            },
            {
                'item': 'Enforce Azure MFA based on a condition',
                'options': [
                    'Azure Monitor',
                    'Azure Security Center',
                    'Azure Active Directory (Azure AD) Identity Protection',
                    'Azure Advanced Threat Protection (ATP)'
                ],
                'answer': 'Azure Active Directory (Azure AD) Identity Protection'
            }
        ]
    }
}

def fix_matching_questions():
    """Matching 문제 정확하게 수정"""
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for q in data['questions']:
        if q['id'] in CORRECT_MATCHING:
            q_num = q['id']
            
            print(f"Q{q_num} 수정 중...")
            
            # 정확한 데이터 적용
            q['questionType'] = 'MATCHING'
            q['question'] = CORRECT_MATCHING[q_num]['question']
            q['matchingItems'] = CORRECT_MATCHING[q_num]['items']
            
            # 기존 필드 정리
            if 'statements' in q:
                del q['statements']
            q['options'] = []
            
            print(f"  ✓ Q{q_num} 수정 완료")
    
    # 저장
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("모든 MATCHING 문제 정확하게 수정 완료!")
    print("="*60)

if __name__ == "__main__":
    fix_matching_questions()

