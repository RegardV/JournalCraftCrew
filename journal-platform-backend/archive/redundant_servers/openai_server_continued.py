# This is a continuation of openai_server.py due to length limitations

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration, request: Request):
    try:
        # Rate limiting based on IP
        client_ip = request.client.host
        if not check_rate_limit(f"register:{client_ip}", 3, 15):
            raise HTTPException(
                status_code=429,
                detail="Too many registration attempts. Please try again later.",
                headers={"Retry-After": "900"}
            )

        # Enhanced input validation
        if not user_data.full_name or len(user_data.full_name.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid name",
                    "message": "Full name must be at least 2 characters long",
                    "field": "full_name"
                }
            )

        if len(user_data.full_name) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid name",
                    "message": "Full name must be less than 100 characters",
                    "field": "full_name"
                }
            )

        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid email",
                    "message": "Please enter a valid email address",
                    "field": "email"
                }
            )

        password_validation = validate_password(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid password",
                    "message": "Password does not meet requirements",
                    "field": "password",
                    "requirements": password_validation["errors"]
                }
            )

        # Validate OpenAI API key if provided
        encrypted_api_key = None
        if user_data.openai_api_key:
            if not user_data.openai_api_key.startswith("sk-"):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid API key",
                        "message": "OpenAI API key must start with 'sk-'",
                        "field": "openai_api_key"
                    }
                )

            # Validate API key with OpenAI
            if not await validate_openai_api_key(user_data.openai_api_key):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid API key",
                        "message": "OpenAI API key is invalid or has insufficient permissions",
                        "field": "openai_api_key"
                    }
                )

            encrypted_api_key = encrypt_api_key(user_data.openai_api_key)

        # Sanitize inputs
        sanitized_name = sanitize_input(user_data.full_name)
        sanitized_email = sanitize_input(user_data.email.lower())

        # Check if user already exists
        for uid, user in data_store["users"].items():
            if user["email"] == sanitized_email:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "User exists",
                        "message": "An account with this email already exists",
                        "field": "email"
                    }
                )

        # Create new user
        user_id = f"user_{len(data_store['users']) + 1}"
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        new_user = {
            "id": user_id,
            "email": sanitized_email,
            "full_name": sanitized_name,
            "openai_api_key": encrypted_api_key,
            "created_at": time.time(),
            "password_hash": password_hash
        }

        data_store["users"][user_id] = new_user

        # Initialize usage stats
        data_store["usage_stats"][user_id] = {
            "total_cost": 0.0,
            "total_tokens": 0,
            "usage_history": []
        }

        save_data(data_store)

        logger.info(f"User registered: {sanitized_email}")

        return {
            "success": True,
            "message": "Registration successful! You can now sign in.",
            "user": {
                "id": user_id,
                "email": sanitized_email,
                "full_name": sanitized_name,
                "has_api_key": encrypted_api_key is not None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Registration failed",
                "message": "An unexpected error occurred during registration"
            }
        )

@app.post("/api/auth/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin, request: Request):
    try:
        # Rate limiting based on IP
        client_ip = request.client.host
        if not check_rate_limit(f"login:{client_ip}", 5, 15):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": "900"}
            )

        # Enhanced input validation
        if not validate_email(login_data.email):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid email",
                    "message": "Please enter a valid email address",
                    "field": "email"
                }
            )

        if not login_data.password or len(login_data.password) < 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid password",
                    "message": "Please enter your password",
                    "field": "password"
                }
            )

        # Find user by email
        user = None
        for uid, user_data in data_store["users"].items():
            if user_data["email"] == login_data.email.lower():
                user = user_data
                break

        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication failed",
                    "message": "Invalid email or password"
                }
            )

        # Verify password
        if user["password_hash"] != hashlib.sha256(login_data.password.encode()).hexdigest():
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication failed",
                    "message": "Invalid email or password"
                }
            )

        # Create token
        token = create_jwt_token(user)

        # Store session
        session_id = str(uuid.uuid4())
        data_store["sessions"][session_id] = {
            "user_id": user["id"],
            "token": token,
            "created_at": time.time(),
            "ip_address": client_ip
        }
        save_data(data_store)

        logger.info(f"User logged in: {login_data.email}")

        return LoginResponse(
            success=True,
            message="Login successful! Welcome back.",
            access_token=token,
            token_type="bearer",
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "has_api_key": user.get("openai_api_key") is not None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Login failed",
                "message": "An unexpected error occurred during login"
            }
        )

# API Key management endpoints
@app.post("/api/user/api-key")
async def update_api_key(api_key_data: APIKeyUpdate, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not api_key_data.openai_api_key.startswith("sk-"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key must start with 'sk-'"
            )

        # Validate API key with OpenAI
        if not await validate_openai_api_key(api_key_data.openai_api_key):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is invalid or has insufficient permissions"
            )

        # Encrypt and store API key
        encrypted_key = encrypt_api_key(api_key_data.openai_api_key)
        data_store["users"][current_user]["openai_api_key"] = encrypted_key
        save_data(data_store)

        return {
            "success": True,
            "message": "API key updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")

@app.delete("/api/user/api-key")
async def delete_api_key(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data_store["users"][current_user]["openai_api_key"] = None
        save_data(data_store)

        return {
            "success": True,
            "message": "API key removed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")

@app.get("/api/user/usage-stats")
async def get_usage_stats(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        stats = data_store["usage_stats"].get(current_user, {
            "total_cost": 0.0,
            "total_tokens": 0,
            "usage_history": []
        })

        return stats

    except Exception as e:
        logger.error(f"Usage stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")

# AI Generation endpoints
@app.get("/api/ai/themes")
async def get_available_themes():
    return {
        "themes": AVAILABLE_THEMES,
        "count": len(AVAILABLE_THEMES)
    }

@app.get("/api/ai/title-styles")
async def get_title_styles():
    return {
        "title_styles": TITLE_STYLES,
        "count": len(TITLE_STYLES)
    }

@app.post("/api/ai/generate-journal")
async def generate_journal(request: AIGenerationRequest, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        user = data_store["users"].get(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user has OpenAI API key
        encrypted_key = user.get("openai_api_key")
        if not encrypted_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key required. Please add your API key in settings."
            )

        # Decrypt API key
        try:
            api_key = decrypt_api_key(encrypted_key)
        except Exception as e:
            logger.error(f"API key decryption error: {e}")
            raise HTTPException(status_code=500, detail="Failed to access API key")

        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Create job record
        data_store["ai_jobs"][job_id] = {
            "id": job_id,
            "theme": request.theme,
            "title_style": request.title_style,
            "description": request.description,
            "status": "pending",
            "progress": 0,
            "created_at": time.time(),
            "user_id": current_user
        }
        save_data(data_store)

        # Start background task
        asyncio.create_task(real_openai_generation(job_id, request.theme, request.title_style, api_key, current_user))

        logger.info(f"AI generation started by user {current_user}: {job_id}")

        return {
            "success": True,
            "message": "AI journal generation started",
            "job_id": job_id,
            "estimated_time": 180,
            "status": "pending"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def real_openai_generation(job_id: str, theme: str, title_style: str, api_key: str, user_id: str):
    """Real OpenAI API integration for journal generation"""
    stages = [
        (10, "🤖 Initializing AI generation..."),
        (25, "📚 Analyzing theme and style patterns..."),
        (40, "✍️ Generating journal content structure..."),
        (60, "🎨 Creating daily journal entries..."),
        (80, "📄 Formatting and organizing content..."),
        (95, "🔧 Finalizing journal design..."),
        (100, "✅ Complete!")
    ]

    client = openai.OpenAI(api_key=api_key)
    total_tokens_used = 0
    total_cost = 0.0

    try:
        for progress, stage in stages:
            if job_id not in data_store["ai_jobs"]:
                return  # Job was cancelled

            data_store["ai_jobs"][job_id]["progress"] = progress
            data_store["ai_jobs"][job_id]["current_stage"] = stage
            save_data(data_store)

            # Generate content based on stage
            if progress == 25:
                # Generate content structure
                system_prompt = f"""
                You are creating a 30-day journal focused on {theme}.
                Style: {title_style}
                Generate a structured outline for daily journal entries.
                Each entry should include:
                - Date and title
                - Main prompt/question
                - Reflection space
                - Optional creative exercise

                Return as JSON format with array of 30 entries.
                """

                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful journal content creator."},
                        {"role": "user", "content": system_prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )

                content_structure = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                total_tokens_used += tokens_used
                total_cost += tokens_used * 0.000002  # Approximate cost for gpt-3.5-turbo

                # Store structure for later use
                data_store["ai_jobs"][job_id]["content_structure"] = content_structure

            elif progress == 60:
                # Generate actual content
                content_structure = data_store["ai_jobs"][job_id].get("content_structure", "")

                content_prompt = f"""
                Based on this structure for a {theme} journal with {title_style} style:

                {content_structure}

                Expand each entry into a complete journal entry. Include:
                - Inspiring quotes related to the theme
                - Thoughtful questions
                - Creative exercises
                - Space for reflection

                Generate complete, ready-to-use content for all 30 days.
                Format as JSON with entries array containing date, title, and content.
                """

                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a creative journal content writer."},
                        {"role": "user", "content": content_prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.8
                )

                journal_content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                total_tokens_used += tokens_used
                total_cost += tokens_used * 0.000002

                data_store["ai_jobs"][job_id]["journal_content"] = journal_content

            # Create completed project at 100%
            if progress == 100:
                project_id = f"project_{uuid.uuid4().hex[:12]}"
                data_store["ai_jobs"][job_id]["status"] = "completed"

                data_store["projects"][project_id] = {
                    "id": project_id,
                    "title": f"{title_style.title()} {theme.title()} Journal",
                    "theme": theme,
                    "description": f"AI-generated {theme} journal with {title_style} style",
                    "status": "completed",
                    "created_at": time.time(),
                    "updated_at": time.time(),
                    "customization": {
                        "layout": "single-column",
                        "font_size": "medium",
                        "color_scheme": "default",
                        "paper_type": "standard",
                        "binding_type": "perfect"
                    },
                    "pages_count": 30,
                    "word_count": 15000,
                    "export_formats": ["pdf", "epub", "kdp"],
                    "job_id": job_id,
                    "user_id": user_id,
                    "content": data_store["ai_jobs"][job_id].get("journal_content", ""),
                    "tokens_used": total_tokens_used,
                    "cost": total_cost
                }

                # Update user usage stats
                if user_id not in data_store["usage_stats"]:
                    data_store["usage_stats"][user_id] = {
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "usage_history": []
                    }

                data_store["usage_stats"][user_id]["total_cost"] += total_cost
                data_store["usage_stats"][user_id]["total_tokens"] += total_tokens_used
                data_store["usage_stats"][user_id]["usage_history"].append({
                    "timestamp": time.time(),
                    "job_id": job_id,
                    "tokens_used": total_tokens_used,
                    "cost": total_cost,
                    "theme": theme,
                    "title_style": title_style
                })

            save_data(data_store)

        except Exception as e:
            logger.error(f"OpenAI generation error for job {job_id}: {e}")
            if job_id in data_store["ai_jobs"]:
                data_store["ai_jobs"][job_id]["status"] = "failed"
                data_store["ai_jobs"][job_id]["error"] = str(e)
                save_data(data_store)

        await asyncio.sleep(2)  # Realistic timing between stages

@app.get("/api/ai/progress/{job_id}")
async def get_generation_progress(job_id: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if job_id not in data_store["ai_jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify job ownership
    job = data_store["ai_jobs"][job_id]
    if job.get("user_id") != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_percentage": job["progress"],
        "current_stage": job.get("current_stage", "Processing..."),
        "estimated_time_remaining": max(0, 180 - (time.time() - job["created_at"])),
        "created_at": job["created_at"]
    }

@app.get("/api/library/projects")
async def get_user_projects(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get projects for current user
    user_projects = []
    for pid, project in data_store["projects"].items():
        if project.get("user_id") == current_user:
            user_projects.append(project)

    return {
        "projects": user_projects,
        "count": len(user_projects),
        "page": 1,
        "total_pages": 1
    }

@app.get("/api/library/projects/{project_id}")
async def get_project_details(project_id: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if project_id not in data_store["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")

    project = data_store["projects"][project_id]
    if project.get("user_id") != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "project": project,
        "success": True
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "journal-platform-openai",
        "timestamp": datetime.utcnow().isoformat(),
        "openai_integration": True,
        "data_stats": {
            "users": len(data_store["users"]),
            "projects": len(data_store["projects"]),
            "active_sessions": len(data_store["sessions"]),
            "ai_jobs": len(data_store["ai_jobs"]),
            "usage_stats": len(data_store["usage_stats"])
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting OpenAI-Powered Server")
    print("📍 BYO API Key System: http://localhost:8000")
    print("🔑 Real OpenAI Integration")
    print("📋 Users:", len(data_store.get('users', [])))
    print("📚 Projects:", len(data_store.get('projects', [])))
    print("🤖 Active AI Jobs:", len(data_store.get('ai_jobs', [])))
    print("💡 Features:")
    print("   - Bring your own OpenAI API key")
    print("   - Real AI journal generation")
    print("   - Cost tracking and usage statistics")
    print("   - Secure key encryption and storage")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )