import streamlit as st
import httpx
from supabase import create_client, Client

# Intercept all httpx sync requests to gracefully handle connection/DNS errors (e.g. database paused)
_orig_send = httpx.Client.send

def _patched_send(self, request, *args, **kwargs):
    try:
        return _orig_send(self, request, *args, **kwargs)
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        is_streamlit = False
        try:
            from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
            is_streamlit = get_script_run_ctx() is not None
        except Exception:
            pass

        if is_streamlit:
            st.error("🚨 **Database Offline**: The connection to Supabase failed. Your database project may be paused or offline. Please log in to the Supabase Dashboard to restore/unpause it.")
            st.stop()
        else:
            raise RuntimeError(
                "Database Connection Error: The Supabase project is paused or offline. "
                "Please restore it in the Supabase Dashboard."
            ) from e

httpx.Client.send = _patched_send

supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)