@echo off
echo =========================================================================
echo Running Automated Test Suite (TC-01 through TC-12)
echo SIH 2026 - Problem Statement SIH26044 - Group G29
echo =========================================================================
pytest backend/tests/ -v
pause
