import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Eye, EyeOff, Loader2, ShieldAlert, Sparkles } from "lucide-react";
import { getLlmSettings, updateLlmSettings, validateLlmSettings } from "../api/interview";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const PAGE_CLASS = "flex-1 w-full max-w-[1600px] mx-auto px-4 py-6 md:px-7 md:py-8 xl:px-10 2xl:px-12";

const EMPTY_FORM = {
  apiBase: "",
  apiKey: "",
  model: "",
};

function buildValidationTone(status) {
  if (status === "success") return "success";
  if (status === "error") return "destructive";
  if (status === "checking") return "blue";
  return "secondary";
}

export default function Settings() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [persistedMeta, setPersistedMeta] = useState({ hasApiKey: false, maskedApiKey: null });
  const [validation, setValidation] = useState({ status: "idle", message: "保存后可检查连通性，新的全局配置会用于后续请求。", checkedAt: null, resolvedModel: null });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    getLlmSettings()
      .then((data) => {
        if (!mounted) return;
        setForm({ apiBase: data.api_base || "", apiKey: "", model: data.model || "" });
        setPersistedMeta({ hasApiKey: !!data.has_api_key, maskedApiKey: data.masked_api_key || null });
      })
      .catch((err) => {
        if (!mounted) return;
        setError("加载设置失败: " + err.message);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const canSave = useMemo(() => {
    return !loading && !saving && form.apiBase.trim() && form.model.trim() && (dirty || form.apiKey.trim());
  }, [dirty, form.apiBase, form.apiKey, form.model, loading, saving]);

  const canValidate = useMemo(() => {
    const hasKey = form.apiKey.trim() || persistedMeta.hasApiKey;
    return !loading && validation.status !== "checking" && form.apiBase.trim() && form.model.trim() && hasKey;
  }, [form.apiBase, form.apiKey, form.model, loading, persistedMeta.hasApiKey, validation.status]);

  const handleFieldChange = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setDirty(true);
    setError("");
    setValidation((current) => current.status === "idle" ? current : { status: "idle", message: "参数已变更，请重新检查连接。", checkedAt: null, resolvedModel: null });
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      const payload = {
        api_base: form.apiBase.trim(),
        model: form.model.trim(),
        api_key: form.apiKey.trim(),
        replace_api_key: !!form.apiKey.trim(),
      };
      const data = await updateLlmSettings(payload);
      setPersistedMeta({ hasApiKey: !!data.has_api_key, maskedApiKey: data.masked_api_key || null });
      setForm((current) => ({ ...current, apiKey: "" }));
      setDirty(false);
      setValidation({
        status: "idle",
        message: "配置已保存，新的全局配置会用于后续请求。",
        checkedAt: null,
        resolvedModel: null,
      });
    } catch (err) {
      setError("保存失败: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    setValidation({ status: "checking", message: "正在检查连接...", checkedAt: null, resolvedModel: null });
    setError("");
    try {
      const data = await validateLlmSettings({
        api_base: form.apiBase.trim(),
        api_key: form.apiKey.trim(),
        model: form.model.trim(),
      });
      setValidation({
        status: "success",
        message: data.message || "连接成功",
        checkedAt: new Date().toLocaleString(),
        resolvedModel: data.resolved_model || null,
      });
    } catch (err) {
      setValidation({
        status: "error",
        message: err.message || "连接检查失败",
        checkedAt: new Date().toLocaleString(),
        resolvedModel: null,
      });
    }
  };

  return (
    <div className={PAGE_CLASS}>
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_360px] 2xl:grid-cols-[minmax(0,1.55fr)_380px]">
        <div className="space-y-5">
          <Card className="overflow-hidden border-border/80 bg-card/76">
            <CardContent className="p-5 md:p-6 xl:p-7">
              <div className="flex flex-col gap-6">
                <div className="border-b border-border/70 pb-4">
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-dim/80">模型连接设置</div>
                  <div className="mt-2 text-2xl font-display font-bold tracking-tight md:text-3xl">LLM 设置</div>
                  <div className="mt-1.5 max-w-3xl text-sm leading-6 text-dim">
                    保存当前系统的全局大模型连接配置，并在提交前做一次在线检测。保存后，后续请求会使用新的全局配置。
                  </div>
                </div>

                <div className="grid gap-4">
                  <div className="space-y-2">
                    <Label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-dim/80">Base URL</Label>
                    <Input
                      className="h-12 rounded-2xl bg-card/90"
                      placeholder="https://your-openai-compatible-endpoint/v1"
                      value={form.apiBase}
                      onChange={(event) => handleFieldChange("apiBase", event.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-3">
                      <Label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-dim/80">API Key</Label>
                      {persistedMeta.hasApiKey && (
                        <span className="text-xs text-dim">当前全局密钥 {persistedMeta.maskedApiKey || "已配置"}</span>
                      )}
                    </div>
                    <div className="relative">
                      <Input
                        type={showApiKey ? "text" : "password"}
                        className="h-12 rounded-2xl bg-card/90 pr-12"
                        placeholder={persistedMeta.hasApiKey ? "留空则保留当前全局 API Key" : "sk-..."}
                        value={form.apiKey}
                        onChange={(event) => handleFieldChange("apiKey", event.target.value)}
                      />
                      <button
                        type="button"
                        onClick={() => setShowApiKey((current) => !current)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-dim hover:text-text"
                        aria-label={showApiKey ? "隐藏 API Key" : "显示 API Key"}
                      >
                        {showApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                    <div className="text-xs text-dim">API Key 仅在服务端保存，并会同步写入当前系统使用的 .env 配置。</div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-dim/80">Model</Label>
                    <Input
                      className="h-12 rounded-2xl bg-card/90"
                      placeholder="gpt-4o-mini"
                      value={form.model}
                      onChange={(event) => handleFieldChange("model", event.target.value)}
                    />
                  </div>
                </div>

                {error && (
                  <div className="rounded-2xl border border-red/20 bg-red/8 px-4 py-3 text-sm text-red">
                    {error}
                  </div>
                )}

                <div className="flex flex-wrap gap-3">
                  <Button onClick={handleSave} disabled={!canSave} className="rounded-2xl px-5">
                    {saving && <Loader2 className="animate-spin" />}
                    保存配置
                  </Button>
                  <Button variant="outline" onClick={handleValidate} disabled={!canValidate} className="rounded-2xl px-5">
                    {validation.status === "checking" && <Loader2 className="animate-spin" />}
                    检查连接
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-5">
          <Card className="border-border/80 bg-[linear-gradient(135deg,rgba(255,255,255,0.94),rgba(244,247,255,0.92))] dark:bg-[linear-gradient(135deg,rgba(24,24,27,0.96),rgba(30,41,59,0.72))]">
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-dim/80">连接检查</div>
                  <div className="mt-2 text-lg font-semibold">当前状态</div>
                </div>
                <Badge variant={buildValidationTone(validation.status)}>
                  {validation.status === "success" && "已通过"}
                  {validation.status === "error" && "检查失败"}
                  {validation.status === "checking" && "检测中"}
                  {validation.status === "idle" && "未检测"}
                </Badge>
              </div>

              <div className={cn(
                "mt-4 rounded-[20px] border px-4 py-4 text-sm leading-6",
                validation.status === "success" && "border-green/20 bg-green/8 text-green",
                validation.status === "error" && "border-red/20 bg-red/8 text-red",
                validation.status === "checking" && "border-blue-500/20 bg-blue-500/8 text-blue-300",
                validation.status === "idle" && "border-border/80 bg-card/72 text-dim"
              )}>
                {validation.status === "success" && <CheckCircle2 className="mb-3" size={18} />}
                {validation.status === "error" && <ShieldAlert className="mb-3" size={18} />}
                {validation.status === "checking" && <Loader2 className="mb-3 animate-spin" size={18} />}
                {validation.status === "idle" && <Sparkles className="mb-3" size={18} />}
                <div>{validation.message}</div>
                {validation.resolvedModel && <div className="mt-2 text-xs opacity-80">模型：{validation.resolvedModel}</div>}
                {validation.checkedAt && <div className="mt-2 text-xs opacity-80">检查时间：{validation.checkedAt}</div>}
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/80 bg-card/76">
            <CardContent className="p-5">
              <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-dim/80">说明</div>
              <div className="mt-3 space-y-3 text-sm leading-6 text-dim">
                <div>1. 这里修改的是当前系统的全局模型连接配置。</div>
                <div>2. 保存后，后续请求会使用新的全局配置。</div>
                <div>3. 在线检测只做轻量连通性检查，不会自动重启服务或容器。</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
