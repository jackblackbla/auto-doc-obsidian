# Auto Documentation with GitHub Actions

코드 변경사항을 자동으로 요약하여 문서화하는 시스템입니다.

## 주요 기능

- GitHub 코드 변경사항(diff) 자동 감지
- DeepSeek API를 통한 코드 변경사항 요약
- Markdown 형식의 문서 자동 생성
- 년/월 기반의 체계적인 문서 관리

## 시스템 구조

```
auto-doc-obsidian/
├── .github/workflows/   # GitHub Actions 설정
│   └── auto-doc.yml    # 자동화 워크플로우
├── scripts/            # 스크립트 파일
│   └── summarize_diff_to_md.py  # 요약 생성 스크립트
└── summaries/          # 생성된 요약 문서
    └── YYYY/          # 연도별 폴더
        └── MM/        # 월별 폴더
            └── YYYY-MM-DD_HH-MM-SS_summary.md
```

## 설정 방법

1. GitHub Secrets 설정
   - Repository Settings → Secrets → Actions
   - `DEEPSEEK_API_KEY` 시크릿 추가

2. 자동 문서화 활성화
   - main 브랜치에 push 이벤트 발생 시 자동 실행
   - `summaries/` 폴더에 마크다운 파일 자동 생성

## 생성되는 문서 형식

각 요약 문서는 다음 정보를 포함합니다:
- 날짜 및 시간 (UTC)
- 브랜치 이름
- 커밋 해시
- 변경사항 요약

예시:
```markdown
# Code Update Summary

- **Date**: 2024-12-29 10:49:48 UTC
- **Branch**: main
- **Commit**: 0853b1ad469ccc...

## Changes Summary
[변경사항 요약 내용]
```

## 주의사항

- `summaries/` 폴더의 파일은 자동 생성되므로 직접 수정하지 않는 것을 권장
- API 요청 실패 시 에러 메시지가 문서에 기록됨

## 향후 개선 계획

- [ ] 대용량 코드 변경 처리 개선
- [ ] 에러 처리 강화
- [ ] 요약 품질 최적화

## 라이센스

MIT License
