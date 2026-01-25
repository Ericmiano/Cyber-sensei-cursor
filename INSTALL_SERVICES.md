# Installing Required Services on Windows

## PostgreSQL Installation

PostgreSQL is **not currently installed** on your system. Here's how to install it:

### Option 1: Official PostgreSQL Installer (Recommended)

1. **Download PostgreSQL 15+**:
   - Visit: https://www.postgresql.org/download/windows/
   - Download the installer (e.g., `postgresql-15.x-windows-x64.exe`)

2. **Run the Installer**:
   - Follow the installation wizard
   - **Important**: Remember the password you set for the `postgres` user
   - Default port: `5432`
   - Install location: Usually `C:\Program Files\PostgreSQL\15`

3. **Add to PATH** (Optional but recommended):
   - Add `C:\Program Files\PostgreSQL\15\bin` to your system PATH
   - This allows using `psql` from any terminal

4. **Install pgvector Extension**:
   - Download from: https://github.com/pgvector/pgvector/releases
   - For PostgreSQL 15 on Windows, download the appropriate `.zip` file
   - Extract and copy:
     - `pgvector.dll` → `C:\Program Files\PostgreSQL\15\lib\`
     - `pgvector.control` and `pgvector--*.sql` → `C:\Program Files\PostgreSQL\15\share\extension\`

5. **Verify Installation**:
   ```powershell
   psql --version
   ```

### Option 2: Using Chocolatey (If you have it)

```powershell
choco install postgresql15
```

## Redis Installation

### Option 1: Memurai (Recommended - Native Windows)

Memurai is the official Redis-compatible solution for Windows:

1. **Download Memurai**:
   - Visit: https://www.memurai.com/get-memurai
   - Download the free developer edition

2. **Install**:
   - Run the installer
   - Choose to install as a Windows service
   - Default port: `6379`
   - Configure firewall rules if prompted

3. **Verify**:
   ```powershell
   redis-cli ping
   # Should return: PONG
   ```

### Option 2: WSL2 (If you have Windows Subsystem for Linux)

If you have WSL2 installed:

```bash
# In WSL terminal
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

Then Redis will be accessible from Windows at `localhost:6379`

### Option 3: Docker (If you have Docker Desktop)

```powershell
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

## Quick Installation Commands

### Using Winget (Windows Package Manager)

If you have winget installed:

```powershell
# Install PostgreSQL
winget install PostgreSQL.PostgreSQL

# Install Memurai (Redis for Windows)
winget install Memurai.Memurai
```

## After Installation

### 1. Start PostgreSQL Service

```powershell
# Check if service exists
Get-Service -Name postgresql*

# Start the service (replace with actual service name)
Start-Service postgresql-x64-15
```

### 2. Start Redis/Memurai

```powershell
# If installed as service, it should start automatically
# Or start manually:
Start-Service Memurai
```

### 3. Verify Services

```powershell
# Check PostgreSQL
psql -U postgres -c "SELECT version();"

# Check Redis
redis-cli ping
```

### 4. Create Database

After PostgreSQL is running:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python scripts\init_db.py
alembic upgrade head
```

## Troubleshooting

### PostgreSQL Connection Issues

- **Service not running**: `Start-Service postgresql-x64-15`
- **Wrong password**: Reset in `pg_hba.conf` or reinstall
- **Port conflict**: Check if port 5432 is in use

### Redis Connection Issues

- **Service not running**: `Start-Service Memurai`
- **Port conflict**: Check if port 6379 is in use
- **WSL Redis**: Ensure WSL is running and Redis service started

## Next Steps

Once both services are installed and running:

1. Update `.env` file if needed (defaults should work)
2. Run database initialization: `python scripts\init_db.py`
3. Start the backend: `uvicorn app.main:app --reload`
4. Start the frontend: `npm run dev`
