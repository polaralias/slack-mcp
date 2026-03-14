package auth

import (
	"context"
	"crypto/subtle"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"go.uber.org/zap"
)

// authKey is a custom context key for storing the auth token.
type authKey struct{}

// withAuthKey adds an auth key to the context.
func withAuthKey(ctx context.Context, auth string) context.Context {
	return context.WithValue(ctx, authKey{}, auth)
}

func configuredAPIKeys(logger *zap.Logger) []string {
	apiKeyMode := strings.ToLower(strings.TrimSpace(os.Getenv("API_KEY_MODE")))
	if apiKeyMode == "disabled" {
		return nil
	}

	var keys []string
	seen := map[string]struct{}{}
	add := func(raw string) {
		token := strings.TrimSpace(raw)
		if token == "" {
			return
		}
		if _, ok := seen[token]; ok {
			return
		}
		seen[token] = struct{}{}
		keys = append(keys, token)
	}

	add(os.Getenv("SLACK_MCP_API_KEY"))

	if legacy := os.Getenv("SLACK_MCP_SSE_API_KEY"); legacy != "" {
		logger.Warn("SLACK_MCP_SSE_API_KEY is deprecated, please use SLACK_MCP_API_KEY or MCP_API_KEY")
		add(legacy)
	}

	add(os.Getenv("MCP_API_KEY"))

	if multi := os.Getenv("MCP_API_KEYS"); multi != "" {
		for _, raw := range strings.Split(multi, ",") {
			add(raw)
		}
	}

	return keys
}

func normalizePresentedToken(token string) string {
	cleaned := strings.TrimSpace(token)
	if strings.HasPrefix(cleaned, "Bearer ") {
		return strings.TrimSpace(strings.TrimPrefix(cleaned, "Bearer "))
	}
	return cleaned
}

func validatePresentedToken(presented string, logger *zap.Logger) (bool, error) {
	configured := configuredAPIKeys(logger)
	if len(configured) == 0 {
		logger.Debug("No HTTP API key configured, skipping authentication",
			zap.String("context", "http"),
		)
		return true, nil
	}

	token := normalizePresentedToken(presented)
	if token == "" {
		logger.Warn("Missing auth token in request",
			zap.String("context", "http"),
		)
		return false, fmt.Errorf("missing auth")
	}

	for _, key := range configured {
		if subtle.ConstantTimeCompare([]byte(key), []byte(token)) == 1 {
			return true, nil
		}
	}

	logger.Warn("Invalid auth token provided",
		zap.String("context", "http"),
	)
	return false, fmt.Errorf("invalid auth token")
}

// Authenticate checks if the request is authenticated based on the provided context.
func validateToken(ctx context.Context, logger *zap.Logger) (bool, error) {
	authHeader, _ := ctx.Value(authKey{}).(string)
	return validatePresentedToken(authHeader, logger)
}

// AuthFromRequest extracts the auth token from the request headers.
func AuthFromRequest(logger *zap.Logger) func(context.Context, *http.Request) context.Context {
	return func(ctx context.Context, r *http.Request) context.Context {
		authHeader := r.Header.Get("Authorization")
		return withAuthKey(ctx, authHeader)
	}
}

// ValidateRequest checks whether an HTTP request is authorized.
func ValidateRequest(r *http.Request, logger *zap.Logger) (bool, error) {
	return validatePresentedToken(r.Header.Get("Authorization"), logger)
}

// RequireRequestAuth protects the full HTTP request lifecycle, including initialize
// and discovery requests that happen before any tool call middleware runs.
func RequireRequestAuth(next http.Handler, logger *zap.Logger) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		authenticated, err := ValidateRequest(r, logger)
		if authenticated {
			next.ServeHTTP(w, r)
			return
		}

		logger.Warn("HTTP request authentication failed",
			zap.String("context", "http"),
			zap.String("path", r.URL.Path),
			zap.String("method", r.Method),
			zap.Error(err),
		)

		w.Header().Set("WWW-Authenticate", `Bearer realm="slack-mcp"`)
		http.Error(w, "Unauthorized", http.StatusUnauthorized)
	})
}

// BuildMiddleware creates a middleware function that ensures authentication based on the provided transport type.
func BuildMiddleware(transport string, logger *zap.Logger) server.ToolHandlerMiddleware {
	return func(next server.ToolHandlerFunc) server.ToolHandlerFunc {
		return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
			logger.Debug("Auth middleware invoked",
				zap.String("context", "http"),
				zap.String("transport", transport),
				zap.String("tool", req.Params.Name),
			)

			if authenticated, err := IsAuthenticated(ctx, transport, logger); !authenticated {
				logger.Error("Authentication failed",
					zap.String("context", "http"),
					zap.String("transport", transport),
					zap.String("tool", req.Params.Name),
					zap.Error(err),
				)
				return nil, err
			}

			logger.Debug("Authentication successful",
				zap.String("context", "http"),
				zap.String("transport", transport),
				zap.String("tool", req.Params.Name),
			)

			return next(ctx, req)
		}
	}
}

// IsAuthenticated public api
func IsAuthenticated(ctx context.Context, transport string, logger *zap.Logger) (bool, error) {
	switch transport {
	case "stdio":
		return true, nil

	case "sse", "http":
		authenticated, err := validateToken(ctx, logger)

		if err != nil {
			logger.Error("HTTP/SSE authentication error",
				zap.String("context", "http"),
				zap.Error(err),
			)
			return false, fmt.Errorf("authentication error: %w", err)
		}

		if !authenticated {
			logger.Warn("HTTP/SSE unauthorized request",
				zap.String("context", "http"),
			)
			return false, fmt.Errorf("unauthorized request")
		}

		return true, nil

	default:
		logger.Error("Unknown transport type",
			zap.String("context", "http"),
			zap.String("transport", transport),
		)
		return false, fmt.Errorf("unknown transport type: %s", transport)
	}
}
