import { useState, useEffect, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import {
  Plus,
  Settings,
  Database,
  RefreshCw,
  Trash2,
  Edit2,
  Play,
  Pause,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ArrowLeft,
  Eye,
  EyeOff
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from 'sonner'

function ProviderForm({ provider, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    name: provider?.name || '',
    provider_type: provider?.provider_type || 'api',
    base_url: provider?.base_url || '',
    api_key: '',
    is_active: provider?.is_active ?? true,
    rate_limit_requests: provider?.rate_limit_requests || 100,
    rate_limit_period: provider?.rate_limit_period || 3600,
    sync_interval_hours: provider?.sync_interval_hours || 24,
    config: JSON.stringify(provider?.config || {}, null, 2)
  })
  const [showApiKey, setShowApiKey] = useState(false)
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)

    try {
      let config = {}
      try {
        config = JSON.parse(formData.config)
      } catch {
        toast.error('Invalid JSON in config field')
        setSaving(false)
        return
      }

      const payload = {
        ...formData,
        config,
        rate_limit_requests: parseInt(formData.rate_limit_requests),
        rate_limit_period: parseInt(formData.rate_limit_period),
        sync_interval_hours: parseInt(formData.sync_interval_hours)
      }

      if (!formData.api_key) {
        delete payload.api_key
      }

      await onSave(payload)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="name">Provider Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., 1build, RSMeans"
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="provider_type">Type</Label>
          <Select
            value={formData.provider_type}
            onValueChange={(value) => setFormData({ ...formData, provider_type: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="api">API</SelectItem>
              <SelectItem value="scraper">Web Scraper</SelectItem>
              <SelectItem value="b2b">B2B Partnership</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="base_url">Base URL</Label>
        <Input
          id="base_url"
          value={formData.base_url}
          onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
          placeholder="https://api.example.com/v1"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="api_key">API Key {provider && '(leave blank to keep existing)'}</Label>
        <div className="relative">
          <Input
            id="api_key"
            type={showApiKey ? 'text' : 'password'}
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            placeholder={provider ? '••••••••' : 'Enter API key'}
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="rate_limit_requests">Rate Limit (requests)</Label>
          <Input
            id="rate_limit_requests"
            type="number"
            value={formData.rate_limit_requests}
            onChange={(e) => setFormData({ ...formData, rate_limit_requests: e.target.value })}
            min="1"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="rate_limit_period">Rate Period (seconds)</Label>
          <Input
            id="rate_limit_period"
            type="number"
            value={formData.rate_limit_period}
            onChange={(e) => setFormData({ ...formData, rate_limit_period: e.target.value })}
            min="1"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="sync_interval_hours">Sync Interval (hours)</Label>
          <Input
            id="sync_interval_hours"
            type="number"
            value={formData.sync_interval_hours}
            onChange={(e) => setFormData({ ...formData, sync_interval_hours: e.target.value })}
            min="1"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="config">Additional Config (JSON)</Label>
        <textarea
          id="config"
          value={formData.config}
          onChange={(e) => setFormData({ ...formData, config: e.target.value })}
          className="w-full h-24 px-3 py-2 border rounded-md font-mono text-sm"
          placeholder='{"supports_volatile": true}'
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          className="rounded"
        />
        <Label htmlFor="is_active">Active</Label>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={saving}>
          {saving ? 'Saving...' : (provider ? 'Update Provider' : 'Create Provider')}
        </Button>
      </DialogFooter>
    </form>
  )
}

function SyncJobStatusBadge({ status }) {
  const variants = {
    pending: { variant: 'secondary', icon: Clock },
    running: { variant: 'default', icon: RefreshCw },
    completed: { variant: 'success', icon: CheckCircle },
    failed: { variant: 'destructive', icon: XCircle }
  }

  const { variant, icon: Icon } = variants[status] || variants.pending

  return (
    <Badge variant={variant} className="flex items-center gap-1">
      <Icon className={`h-3 w-3 ${status === 'running' ? 'animate-spin' : ''}`} />
      {status}
    </Badge>
  )
}

export function AdminPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth()
  const navigate = useNavigate()

  const [providers, setProviders] = useState([])
  const [syncJobs, setSyncJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [jobsLoading, setJobsLoading] = useState(true)

  const [showProviderDialog, setShowProviderDialog] = useState(false)
  const [editingProvider, setEditingProvider] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  const getAuthHeaders = useCallback(() => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  }, [])

  const fetchProviders = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/providers')
      if (response.ok) {
        const data = await response.json()
        setProviders(data.providers)
      }
    } catch (err) {
      toast.error('Failed to fetch providers')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchSyncJobs = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/sync-jobs?per_page=50')
      if (response.ok) {
        const data = await response.json()
        setSyncJobs(data.jobs)
      }
    } catch (err) {
      toast.error('Failed to fetch sync jobs')
    } finally {
      setJobsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/search')
      return
    }

    if (isAuthenticated) {
      fetchProviders()
      fetchSyncJobs()
    }
  }, [authLoading, isAuthenticated, navigate, fetchProviders, fetchSyncJobs])

  const handleCreateProvider = async (data) => {
    try {
      const response = await fetch('/api/v1/providers', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
      })

      if (response.ok) {
        toast.success('Provider created successfully')
        setShowProviderDialog(false)
        fetchProviders()
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to create provider')
      }
    } catch (err) {
      toast.error('Failed to create provider')
    }
  }

  const handleUpdateProvider = async (data) => {
    try {
      const response = await fetch(`/api/v1/providers/${editingProvider.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
      })

      if (response.ok) {
        toast.success('Provider updated successfully')
        setEditingProvider(null)
        fetchProviders()
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to update provider')
      }
    } catch (err) {
      toast.error('Failed to update provider')
    }
  }

  const handleDeleteProvider = async (providerId) => {
    try {
      const response = await fetch(`/api/v1/providers/${providerId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      })

      if (response.ok) {
        toast.success('Provider deleted successfully')
        setDeleteConfirm(null)
        fetchProviders()
      } else {
        toast.error('Failed to delete provider')
      }
    } catch (err) {
      toast.error('Failed to delete provider')
    }
  }

  const handleTriggerSync = async (providerId, jobType = 'full') => {
    try {
      const response = await fetch(`/api/v1/providers/${providerId}/sync`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ job_type: jobType })
      })

      if (response.ok) {
        const data = await response.json()
        toast.success(`Sync job queued: ${data.task_id}`)
        fetchSyncJobs()
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to trigger sync')
      }
    } catch (err) {
      toast.error('Failed to trigger sync')
    }
  }

  const handleToggleActive = async (provider) => {
    try {
      const response = await fetch(`/api/v1/providers/${provider.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ is_active: !provider.is_active })
      })

      if (response.ok) {
        toast.success(`Provider ${!provider.is_active ? 'activated' : 'deactivated'}`)
        fetchProviders()
      }
    } catch (err) {
      toast.error('Failed to update provider')
    }
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/search" className="text-gray-500 hover:text-gray-700">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div className="flex items-center gap-3">
                <Settings className="h-6 w-6 text-gray-700" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Admin Panel</h1>
                  <p className="text-sm text-gray-500">Manage data integrations and providers</p>
                </div>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Logged in as <span className="font-medium">{user?.email}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <Tabs defaultValue="providers">
          <TabsList>
            <TabsTrigger value="providers" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Data Providers
            </TabsTrigger>
            <TabsTrigger value="jobs" className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Sync Jobs
            </TabsTrigger>
          </TabsList>

          <TabsContent value="providers" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Data Providers</CardTitle>
                    <CardDescription>Configure API integrations and data sources</CardDescription>
                  </div>
                  <Button onClick={() => setShowProviderDialog(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Provider
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {providers.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No data providers configured</p>
                    <p className="text-sm">Add your first provider to start syncing material prices</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Last Sync</TableHead>
                        <TableHead>Sync Interval</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {providers.map((provider) => (
                        <TableRow key={provider.id}>
                          <TableCell className="font-medium">{provider.name}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{provider.provider_type}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={provider.is_active ? 'success' : 'secondary'}>
                              {provider.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {provider.last_sync_at
                              ? new Date(provider.last_sync_at).toLocaleString()
                              : 'Never'}
                          </TableCell>
                          <TableCell>{provider.sync_interval_hours}h</TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleToggleActive(provider)}
                                title={provider.is_active ? 'Deactivate' : 'Activate'}
                              >
                                {provider.is_active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleTriggerSync(provider.id)}
                                disabled={!provider.is_active}
                                title="Trigger Sync"
                              >
                                <RefreshCw className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setEditingProvider(provider)}
                                title="Edit"
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setDeleteConfirm(provider)}
                                title="Delete"
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="jobs" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Sync Job History</CardTitle>
                    <CardDescription>Monitor data synchronization status</CardDescription>
                  </div>
                  <Button variant="outline" onClick={fetchSyncJobs}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {jobsLoading ? (
                  <div className="space-y-2">
                    {[1, 2, 3].map(i => <Skeleton key={i} className="h-12 w-full" />)}
                  </div>
                ) : syncJobs.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No sync jobs yet</p>
                    <p className="text-sm">Jobs will appear here when you trigger a sync</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Provider</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Items</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Completed</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {syncJobs.map((job) => (
                        <TableRow key={job.id}>
                          <TableCell className="font-mono text-sm">{job.id}</TableCell>
                          <TableCell>
                            {providers.find(p => p.id === job.provider_id)?.name || job.provider_id}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{job.job_type}</Badge>
                          </TableCell>
                          <TableCell>
                            <SyncJobStatusBadge status={job.status} />
                          </TableCell>
                          <TableCell>
                            {job.items_processed !== null && (
                              <span>
                                {job.items_processed} processed
                                {job.items_failed > 0 && (
                                  <span className="text-red-500"> / {job.items_failed} failed</span>
                                )}
                              </span>
                            )}
                          </TableCell>
                          <TableCell>
                            {job.started_at
                              ? new Date(job.started_at).toLocaleString()
                              : '-'}
                          </TableCell>
                          <TableCell>
                            {job.completed_at
                              ? new Date(job.completed_at).toLocaleString()
                              : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      <Dialog open={showProviderDialog} onOpenChange={setShowProviderDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Add Data Provider</DialogTitle>
            <DialogDescription>
              Configure a new data source for material pricing
            </DialogDescription>
          </DialogHeader>
          <ProviderForm
            onSave={handleCreateProvider}
            onCancel={() => setShowProviderDialog(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={!!editingProvider} onOpenChange={() => setEditingProvider(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Provider</DialogTitle>
            <DialogDescription>
              Update provider configuration
            </DialogDescription>
          </DialogHeader>
          {editingProvider && (
            <ProviderForm
              provider={editingProvider}
              onSave={handleUpdateProvider}
              onCancel={() => setEditingProvider(null)}
            />
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Provider</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{deleteConfirm?.name}"? This action cannot be undone.
              All associated sync jobs and price sources will also be deleted.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirm(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleDeleteProvider(deleteConfirm?.id)}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
