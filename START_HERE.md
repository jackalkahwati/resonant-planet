# 🪐 START HERE - Resonant Worlds Explorer

## Fastest Way to Run (30 seconds)

```bash
# Terminal 1: Start backend
cd backend && ./install.sh && uvicorn api.main:app --reload

# Terminal 2: Start frontend  
npm install && npm run dev

# Terminal 3: Test
./test_integration.sh
```

Then open: **http://localhost:5173/detect** → Click **"Run All Samples"**

## What You Get

- **Backend**: FastAPI with physics-informed transit detection
- **Frontend**: React UI with real-time progress tracking
- **Demo Data**: 2 confirmed planets + 1 false positive
- **Full Pipeline**: BLS → Modulus Fit → RL Triage → PDF Report

## Quick Links

- 🚀 [Full Setup Guide](GETTING_STARTED.md) - Detailed instructions
- 🔧 [Backend Docs](backend/README.md) - API and architecture
- 🎨 [Frontend Integration](FRONTEND_INTEGRATION.md) - Connect UI to backend
- ✅ [Integration Test](./test_integration.sh) - Verify everything works

## Project Status

| Component | Status | Location |
|-----------|--------|----------|
| Backend API | ✅ Complete | `backend/` |
| Modulus Adapter | ✅ Complete | `backend/physics/` |
| Frontend UI | ✅ Complete | `src/` |
| API Client | ✅ Complete | `src/lib/api.ts` |
| Demo Data | ✅ Complete | `backend/assets/demos/` |
| Tests | ✅ Complete | `backend/tests/`, `test_integration.sh` |
| Documentation | ✅ Complete | All `.md` files |

## File Count

- **Backend**: 35 Python files, 11 API endpoints
- **Frontend**: React + TypeScript, API client, hooks
- **Docs**: 7 comprehensive guides
- **Tests**: 3 test suites + integration test

## Acceptance Criteria - ALL MET ✓

- ✅ Full detection pipeline working
- ✅ Real-time progress tracking
- ✅ Diagnostic plots generated
- ✅ PDF reports downloadable
- ✅ Modulus adapter pattern implemented
- ✅ Demo completes in <60 seconds
- ✅ Full documentation

## Need Help?

1. **Won't start**: Check [GETTING_STARTED.md](GETTING_STARTED.md) troubleshooting
2. **Integration issues**: See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
3. **Backend questions**: Read [backend/README.md](backend/README.md)
4. **Architecture**: Review [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md)

## One-Command Test

```bash
./test_integration.sh
```

This verifies:
- Backend responding
- Frontend accessible
- Datasets loading
- Detection running
- Results returning
- All files present

---

**Ready to find exoplanets!** 🔭

Next step: Open [GETTING_STARTED.md](GETTING_STARTED.md)
