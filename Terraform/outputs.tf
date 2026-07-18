output "public_ip" {
  value       = aws_instance.app_server.public_ip
  description = "The public IP address of your production host"
}

output "api_stream_endpoint" {
  value       = "http://${aws_instance.app_server.public_ip}:8000/api/v1/agent/stream"
  description = "The streaming API endpoint for your frontend hook"
}